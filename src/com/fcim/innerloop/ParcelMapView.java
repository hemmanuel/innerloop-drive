package com.fcim.innerloop;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.location.Location;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.view.ViewConfiguration;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

final class ParcelMapView extends View {
    private static final double R = 6378137.0;
    private static final double WORLD = 2.0 * Math.PI * R;
    private static final int SAT_ZOOM = 16;
    private static final int[] PRIORITY = {
            Color.rgb(145, 145, 145), Color.rgb(255, 193, 7),
            Color.rgb(255, 128, 0), Color.rgb(229, 57, 53)};

    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint text = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Matrix bitmapMatrix = new Matrix();
    private final TileStore tiles;
    private ParcelData data;
    private List<ParcelData.Feature> visible = new ArrayList<>();
    private float visibleX = Float.NaN, visibleY, visibleRadius;

    private double originX, originY;
    private double fixX, fixY, shownX, shownY;
    private double velocityX, velocityY;
    private float speed, accuracy = 20f, heading, shownHeading;
    private boolean hasPosition, hasHeading, headingInitialized, pov = true;
    private boolean satellite = true, follow = true;
    private long fixElapsedNanos, lastFrameNanos;
    private int fixCount;
    private float zoom = 17f;
    private String nearestPick = "";
    private Location pendingLocation;
    interface SelectionListener { void selected(ParcelData.Feature feature); }
    private SelectionListener selectionListener;
    private String pendingFocusId;
    private java.util.Set<String> savedSites = new java.util.HashSet<>();
    void setSelectionListener(SelectionListener listener) {selectionListener=listener;}
    void setSavedSites(java.util.Set<String> sites) {savedSites=sites;updateNearestPick();invalidate();}
    private boolean isSaved(ParcelData.Feature f) {return savedSites.contains(f.siteId);}
    void focusSite(String id) {
        if(data==null){pendingFocusId=id;return;}
        for(ParcelData.Feature f:data.features)if(f.siteId.equals(id)) {
            manualCameraX=(f.minX+f.maxX)*.5;manualCameraY=(f.minY+f.maxY)*.5;
            follow=false;pov=false;zoom=18;visibleX=Float.NaN;invalidate();return;
        }
    }
    private double renderCameraX, renderCameraY, renderBearing;
    private double manualCameraX, manualCameraY;
    private float lastTouchX, lastTouchY, downTouchX, downTouchY;
    private boolean dragging, scaling;
    private final float touchSlop;
    private final ScaleGestureDetector scaleDetector;

    private final RectF povButton = new RectF();
    private final RectF baseButton = new RectF();
    private final RectF followButton = new RectF();
    private final RectF minusButton = new RectF();
    private final RectF plusButton = new RectF();

    ParcelMapView(Context context) {
        super(context);
        setLayerType(View.LAYER_TYPE_HARDWARE, null);
        setBackgroundColor(Color.rgb(18, 22, 24));
        tiles = new TileStore(context, this);
        touchSlop = ViewConfiguration.get(context).getScaledTouchSlop();
        scaleDetector = new ScaleGestureDetector(context, new ScaleGestureDetector.SimpleOnScaleGestureListener() {
            @Override public boolean onScaleBegin(ScaleGestureDetector detector) {
                beginManualCamera();
                scaling = true;
                return true;
            }
            @Override public boolean onScale(ScaleGestureDetector detector) {
                float oldScale = metresScale(zoom);
                double[] fixed = screenOffsetToWorld(detector.getFocusX(), detector.getFocusY(), oldScale, renderBearing);
                double fixedX = manualCameraX + fixed[0], fixedY = manualCameraY + fixed[1];
                zoom = Math.max(15.0f, Math.min(19.5f,
                        zoom + (float)(Math.log(detector.getScaleFactor()) / Math.log(2.0))));
                float newScale = metresScale(zoom);
                double[] after = screenOffsetToWorld(detector.getFocusX(), detector.getFocusY(), newScale, renderBearing);
                manualCameraX = fixedX - after[0];
                manualCameraY = fixedY - after[1];
                visibleX = Float.NaN;
                postInvalidateOnAnimation();
                return true;
            }
        });
        text.setTypeface(android.graphics.Typeface.create("sans", android.graphics.Typeface.BOLD));
        new Thread(new Runnable() {
            @Override public void run() {
                try {
                    final ParcelData loaded = ParcelData.load(getContext().getAssets());
                    post(new Runnable() {
                        @Override public void run() {
                            data = loaded;
                            originX = mercatorX(loaded.originLon);
                            originY = mercatorY(loaded.originLat);
                            visibleX = Float.NaN;
                            if (pendingLocation != null) {
                                Location location = pendingLocation;
                                pendingLocation = null;
                                setLocation(location);
                            }
                            if(pendingFocusId!=null){focusSite(pendingFocusId);pendingFocusId=null;}
                            invalidate();
                        }
                    });
                } catch (final Exception error) {
                    post(new Runnable() {
                        @Override public void run() { nearestPick = "Parcel load failed: " + error.getMessage(); invalidate(); }
                    });
                }
            }
        }, "parcel-loader").start();
    }

    void setLocation(Location location) {
        if (data == null) {
            pendingLocation = new Location(location);
            return;
        }
        double x = mercatorX(location.getLongitude()) - originX;
        double y = mercatorY(location.getLatitude()) - originY;
        long elapsed = location.getElapsedRealtimeNanos();
        float newSpeed = location.hasSpeed() ? location.getSpeed() : 0f;
        float newHeading = location.hasBearing() ? location.getBearing() : heading;

        if (!hasPosition) {
            shownX = x;
            shownY = y;
            hasPosition = true;
        }
        fixX = x;
        fixY = y;
        speed = newSpeed;
        accuracy = location.hasAccuracy() ? location.getAccuracy() : 20f;
        if (location.hasBearing() && newSpeed >= 0.7f) {
            heading = normalize(newHeading);
            hasHeading = true;
            if (!headingInitialized) {
                shownHeading = heading;
                headingInitialized = true;
            }
        }
        if (hasHeading && newSpeed >= 0.4f) {
            double radians = Math.toRadians(heading);
            velocityX = Math.sin(radians) * newSpeed;
            velocityY = Math.cos(radians) * newSpeed;
        } else {
            velocityX = velocityY = 0;
        }
        fixElapsedNanos = elapsed > 0 ? elapsed : SystemClock.elapsedRealtimeNanos();
        fixCount++;
        updateNearestPick();
        postInvalidateOnAnimation();
    }

    private void updateNearestPick() {
        if (data == null || !hasPosition) return;
        ParcelData.Feature best = null;
        double bestDistance = Double.MAX_VALUE;
        for (ParcelData.Feature feature : data.features) {
            if (!isSaved(feature)) continue;
            double dx = (feature.minX + feature.maxX) * .5 - fixX;
            double dy = (feature.minY + feature.maxY) * .5 - fixY;
            double distance = Math.hypot(dx, dy);
            if (distance < bestDistance) { bestDistance = distance; best = feature; }
        }
        nearestPick = best == null ? "No picks loaded" : String.format(Locale.US,
                "Nearest ★ %.1f mi · %s", bestDistance / 1609.344, shortAddress(best.address));
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        long now = SystemClock.elapsedRealtimeNanos();
        double dt = lastFrameNanos == 0 ? 0 : Math.min(.1, (now - lastFrameNanos) / 1e9);
        lastFrameNanos = now;
        double age = hasPosition ? Math.max(0, (now - fixElapsedNanos) / 1e9) : 0;
        if (hasPosition) {
            if (hasHeading && dt > 0) {
                double turnAlpha = 1.0 - Math.exp(-dt / .30);
                shownHeading = normalize((float)(shownHeading + angleDelta(shownHeading, heading) * turnAlpha));
            }
            double prediction = Math.min(age, 2.0);
            double wantedX = fixX + velocityX * prediction;
            double wantedY = fixY + velocityY * prediction;
            double error = Math.hypot(wantedX - shownX, wantedY - shownY);
            if (error > 250) { shownX = wantedX; shownY = wantedY; }
            else if (dt > 0) {
                double alpha = 1.0 - Math.exp(-dt / .24);
                shownX += (wantedX - shownX) * alpha;
                shownY += (wantedY - shownY) * alpha;
            }
        }

        float scale = metresScale(zoom);
        double mapBearing = pov && hasHeading ? shownHeading : 0;
        double cameraX, cameraY;
        if (follow) {
            cameraX = shownX;
            cameraY = shownY;
            if (pov && hasHeading) {
                double ahead = getHeight() * .20 / scale;
                cameraX += Math.sin(Math.toRadians(shownHeading)) * ahead;
                cameraY += Math.cos(Math.toRadians(shownHeading)) * ahead;
            }
        } else {
            cameraX = manualCameraX;
            cameraY = manualCameraY;
        }
        renderCameraX = cameraX;
        renderCameraY = cameraY;
        renderBearing = mapBearing;

        if ((hasPosition || !follow) && data != null) {
            drawBaseTiles(canvas, cameraX, cameraY, mapBearing, scale);
            updateVisible(cameraX, cameraY, scale);
            drawParcels(canvas, cameraX, cameraY, mapBearing, scale);
            drawLabels(canvas, cameraX, cameraY, mapBearing, scale);
            if(hasPosition)drawVehicle(canvas, cameraX, cameraY, mapBearing, scale, age);
        }
        drawHud(canvas, age);
        if (hasPosition) postInvalidateOnAnimation();
    }

    private void updateVisible(double cameraX, double cameraY, float scale) {
        float radius = (float)(Math.hypot(getWidth(), getHeight()) * .58 / scale + 120);
        if (!Float.isNaN(visibleX) && Math.hypot(cameraX - visibleX, cameraY - visibleY) < 70
                && Math.abs(radius - visibleRadius) < 30) return;
        ArrayList<ParcelData.Feature> next = new ArrayList<>();
        float left = (float)cameraX - radius, right = (float)cameraX + radius;
        float bottom = (float)cameraY - radius, top = (float)cameraY + radius;
        for (ParcelData.Feature feature : data.features)
            if (feature.intersects(left, bottom, right, top)) next.add(feature);
        visible = next;
        visibleX = (float)cameraX;
        visibleY = (float)cameraY;
        visibleRadius = radius;
    }

    private void drawBaseTiles(Canvas canvas, double cameraX, double cameraY, double bearing, float scale) {
        int tileZoom = satellite ? SAT_ZOOM : Math.max(15, Math.min(19, Math.round(zoom)));
        double radius = Math.hypot(getWidth(), getHeight()) * .65 / scale;
        double globalX = cameraX + originX, globalY = cameraY + originY;
        int n = 1 << tileZoom;
        int minX = clamp(tileX(globalX - radius, n) - 1, 0, n - 1);
        int maxX = clamp(tileX(globalX + radius, n) + 1, 0, n - 1);
        int minY = clamp(tileY(globalY + radius, n) - 1, 0, n - 1);
        int maxY = clamp(tileY(globalY - radius, n) + 1, 0, n - 1);
        float tileWorld = (float)(WORLD / n);
        for (int tx = minX; tx <= maxX; tx++) for (int ty = minY; ty <= maxY; ty++) {
            Bitmap bitmap = satellite ? tiles.getSatellite(tileZoom, tx, ty) : tiles.getMap(tileZoom, tx, ty);
            if (bitmap == null) continue;
            double west = -Math.PI * R + tx * tileWorld - originX;
            double north = Math.PI * R - ty * tileWorld - originY;
            float[] source = {0, 0, bitmap.getWidth(), 0, 0, bitmap.getHeight()};
            float[] target = new float[6];
            project(west, north, cameraX, cameraY, bearing, scale, target, 0);
            project(west + tileWorld, north, cameraX, cameraY, bearing, scale, target, 2);
            project(west, north - tileWorld, cameraX, cameraY, bearing, scale, target, 4);
            bitmapMatrix.setPolyToPoly(source, 0, target, 0, 3);
            paint.setAlpha(255);
            paint.setFilterBitmap(true);
            canvas.drawBitmap(bitmap, bitmapMatrix, paint);
        }
    }

    private void drawParcels(Canvas canvas, double cameraX, double cameraY, double bearing, float scale) {
        canvas.save();
        canvas.translate(getWidth() * .5f, getHeight() * .5f);
        canvas.rotate((float)-bearing);
        canvas.scale(scale, -scale);
        canvas.translate((float)-cameraX, (float)-cameraY);

        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(1.1f / scale);
        paint.setColor(Color.argb(175, 210, 220, 224));
        for (ParcelData.Feature feature : visible) if (feature.kind == 0) canvas.drawPath(feature.path, paint);

        for (ParcelData.Feature feature : visible) {
            if (feature.kind == 0 && !isSaved(feature)) continue;
            int color = isSaved(feature) ? Color.rgb(255, 214, 0) : PRIORITY[feature.priority];
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(withAlpha(color, feature.priority == 0 ? 58 : 105));
            canvas.drawPath(feature.path, paint);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth((isSaved(feature) ? 5f : 2.3f) / scale);
            paint.setColor(withAlpha(color, 245));
            canvas.drawPath(feature.path, paint);
        }
        canvas.restore();
    }

    private void drawLabels(Canvas canvas, double cameraX, double cameraY, double bearing, float scale) {
        if (zoom < 16.8f) return;
        text.setTextAlign(Paint.Align.CENTER);
        text.setTextSize(dp(12));
        text.setColor(Color.WHITE);
        text.setShadowLayer(dp(2), 0, 0, Color.BLACK);
        float[] point = new float[2];
        for (ParcelData.Feature feature : visible) {
            if ((feature.kind == 0 && !isSaved(feature)) || feature.area <= 0) continue;
            project((feature.minX + feature.maxX) * .5, (feature.minY + feature.maxY) * .5,
                    cameraX, cameraY, bearing, scale, point, 0);
            if (point[0] < -30 || point[0] > getWidth() + 30 || point[1] < -20 || point[1] > getHeight() + 20) continue;
            canvas.drawText(areaLabel(feature.area), point[0], point[1] + dp(4), text);
        }
        text.clearShadowLayer();
    }

    private void drawVehicle(Canvas canvas, double cameraX, double cameraY, double bearing, float scale, double age) {
        float[] point = new float[2];
        project(shownX, shownY, cameraX, cameraY, bearing, scale, point, 0);
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.argb(42, 26, 115, 232));
        canvas.drawCircle(point[0], point[1], Math.max(dp(10), accuracy * scale), paint);
        paint.setColor(age > 5 ? Color.rgb(150, 170, 190) : Color.rgb(26, 115, 232));
        canvas.drawCircle(point[0], point[1], dp(10), paint);
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(dp(3));
        paint.setColor(Color.WHITE);
        canvas.drawCircle(point[0], point[1], dp(10), paint);
        if (hasHeading) {
            float angle = (float)Math.toRadians(shownHeading - bearing);
            float ux = (float)Math.sin(angle), uy = (float)-Math.cos(angle);
            Path arrow = new Path();
            arrow.moveTo(point[0] + ux * dp(22), point[1] + uy * dp(22));
            arrow.lineTo(point[0] - uy * dp(8) - ux * dp(5), point[1] + ux * dp(8) - uy * dp(5));
            arrow.lineTo(point[0] + uy * dp(8) - ux * dp(5), point[1] - ux * dp(8) - uy * dp(5));
            arrow.close();
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(Color.rgb(26, 115, 232));
            canvas.drawPath(arrow, paint);
        }
    }

    private void drawHud(Canvas canvas, double age) {
        float margin = dp(14), buttonH = dp(48), gap = dp(8);
        povButton.set(margin, margin, margin + dp(116), margin + buttonH);
        baseButton.set(povButton.right + gap, margin, povButton.right + gap + dp(116), margin + buttonH);
        followButton.set(baseButton.right + gap, margin, baseButton.right + gap + dp(100), margin + buttonH);
        minusButton.set(getWidth() - margin - dp(104), margin, getWidth() - margin - dp(56), margin + buttonH);
        plusButton.set(getWidth() - margin - dp(48), margin, getWidth() - margin, margin + buttonH);
        drawButton(canvas, povButton, pov ? "POV ↑" : "North ↑", pov);
        drawButton(canvas, baseButton, satellite ? "Satellite" : "Map", satellite);
        drawButton(canvas, followButton, "Follow", follow);
        drawButton(canvas, minusButton, "−", false);
        drawButton(canvas, plusButton, "+", false);

        text.setTextAlign(Paint.Align.LEFT);
        text.setTextSize(dp(15));
        text.setColor(Color.WHITE);
        text.setShadowLayer(dp(3), 0, 0, Color.BLACK);
        String status;
        if (!hasPosition) status = "Waiting for GPS…";
        else if (age > 5) status = String.format(Locale.US, "GPS stale · %.0f sec", age);
        else status = String.format(Locale.US, "GPS %.0f m · %.0f mph · fix %d", accuracy, speed * 2.23694, fixCount);
        canvas.drawText(status, margin, getHeight() - dp(40), text);
        canvas.drawText(data == null ? "Loading all parcels…" : nearestPick,
                margin, getHeight() - dp(17), text);
        if (!satellite) {
            text.setTextAlign(Paint.Align.RIGHT);
            text.setTextSize(dp(11));
            canvas.drawText("Tiles © Esri", getWidth() - margin, getHeight() - dp(17), text);
        }
        text.clearShadowLayer();
    }

    private void drawButton(Canvas canvas, RectF bounds, String label, boolean active) {
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(active ? Color.argb(235, 26, 115, 232) : Color.argb(220, 35, 39, 42));
        canvas.drawRoundRect(bounds, dp(8), dp(8), paint);
        text.setTextAlign(Paint.Align.CENTER);
        text.setTextSize(dp(17));
        text.setColor(Color.WHITE);
        canvas.drawText(label, bounds.centerX(), bounds.centerY() + dp(6), text);
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        scaleDetector.onTouchEvent(event);
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN) {
            downTouchX = lastTouchX = event.getX();
            downTouchY = lastTouchY = event.getY();
            dragging = false;
            return true;
        }
        if (action == MotionEvent.ACTION_MOVE && event.getPointerCount() == 1 && !scaleDetector.isInProgress()) {
            float x = event.getX(), y = event.getY();
            if (!dragging && Math.hypot(x - downTouchX, y - downTouchY) > touchSlop) {
                beginManualCamera();
                dragging = true;
            }
            if (dragging) panBy(x - lastTouchX, y - lastTouchY);
            lastTouchX = x;
            lastTouchY = y;
            return true;
        }
        if (action == MotionEvent.ACTION_UP && !dragging && !scaling && !scaleDetector.isInProgress()) {
            float x = event.getX(), y = event.getY();
            if (povButton.contains(x, y)) pov = !pov;
            else if (baseButton.contains(x, y)) satellite = !satellite;
            else if (followButton.contains(x, y)) follow = true;
            else if (minusButton.contains(x, y)) changeZoom(-.5f);
            else if (plusButton.contains(x, y)) changeZoom(.5f);
            else if(selectionListener!=null && data!=null) {
                double[] offset=screenOffsetToWorld(x,y,metresScale(zoom),renderBearing);
                int wx=(int)Math.round(renderCameraX+offset[0]),wy=(int)Math.round(renderCameraY+offset[1]);
                ParcelData.Feature chosen=null;
                for(ParcelData.Feature f:visible) {
                    if(!f.intersects(wx,wy,wx,wy))continue;
                    android.graphics.Region region=new android.graphics.Region();
                    region.setPath(f.path,new android.graphics.Region((int)Math.floor(f.minX)-1,(int)Math.floor(f.minY)-1,
                        (int)Math.ceil(f.maxX)+1,(int)Math.ceil(f.maxY)+1));
                    if(region.contains(wx,wy) && (chosen==null || f.kind>chosen.kind || (f.kind==chosen.kind && f.area<chosen.area)))chosen=f;
                }
                if(chosen!=null)selectionListener.selected(chosen);
            }
            invalidate();
        }
        if (action == MotionEvent.ACTION_CANCEL || action == MotionEvent.ACTION_UP) {
            dragging = false;
            scaling = false;
        }
        return true;
    }

    private void beginManualCamera() {
        if (follow) {
            manualCameraX = renderCameraX;
            manualCameraY = renderCameraY;
            follow = false;
        }
    }

    private void panBy(float screenDx, float screenDy) {
        double angle = Math.toRadians(renderBearing);
        double cos = Math.cos(angle), sin = Math.sin(angle);
        double rotatedX = cos * screenDx - sin * screenDy;
        double rotatedY = sin * screenDx + cos * screenDy;
        float scale = metresScale(zoom);
        manualCameraX -= rotatedX / scale;
        manualCameraY += rotatedY / scale;
        visibleX = Float.NaN;
        postInvalidateOnAnimation();
    }

    private void changeZoom(float amount) {
        zoom = Math.max(15.0f, Math.min(19.5f, zoom + amount));
        visibleX = Float.NaN;
    }

    private double[] screenOffsetToWorld(float screenX, float screenY, float scale, double bearing) {
        double dx = screenX - getWidth() * .5;
        double dy = screenY - getHeight() * .5;
        double angle = Math.toRadians(bearing);
        double cos = Math.cos(angle), sin = Math.sin(angle);
        double rotatedX = cos * dx - sin * dy;
        double rotatedY = sin * dx + cos * dy;
        return new double[]{rotatedX / scale, -rotatedY / scale};
    }

    void close() { tiles.close(); }

    private void project(double x, double y, double cameraX, double cameraY,
                         double bearing, float scale, float[] output, int offset) {
        double dx = (x - cameraX) * scale;
        double dy = -(y - cameraY) * scale;
        double angle = Math.toRadians(-bearing);
        double cos = Math.cos(angle), sin = Math.sin(angle);
        output[offset] = (float)(getWidth() * .5 + cos * dx - sin * dy);
        output[offset + 1] = (float)(getHeight() * .5 + sin * dx + cos * dy);
    }

    private static float metresScale(float zoom) {
        return (float)(256.0 * Math.pow(2.0, zoom) / WORLD);
    }
    private static double mercatorX(double lon) { return R * Math.toRadians(lon); }
    private static double mercatorY(double lat) {
        lat = Math.max(-85.05112878, Math.min(85.05112878, lat));
        return R * Math.log(Math.tan(Math.PI / 4 + Math.toRadians(lat) / 2));
    }
    private static int tileX(double worldX, int n) { return (int)Math.floor((worldX + Math.PI * R) / WORLD * n); }
    private static int tileY(double worldY, int n) { return (int)Math.floor((Math.PI * R - worldY) / WORLD * n); }
    private static int clamp(int value, int low, int high) { return Math.max(low, Math.min(high, value)); }
    private static float normalize(float angle) { angle %= 360f; return angle < 0 ? angle + 360f : angle; }
    private static float angleDelta(float from, float to) { return (to - from + 540f) % 360f - 180f; }
    private static int withAlpha(int color, int alpha) { return (color & 0x00ffffff) | (alpha << 24); }
    private float dp(float value) { return value * getResources().getDisplayMetrics().density; }
    private static String areaLabel(float area) {
        return area >= 43560 ? String.format(Locale.US, "%.1f ac", area / 43560f)
                : area >= 10000 ? String.format(Locale.US, "%.0fk", area / 1000f)
                : String.format(Locale.US, "%.1fk", area / 1000f);
    }
    private static String shortAddress(String address) {
        int split = address.indexOf(';');
        return split < 0 ? address : address.substring(0, split) + " +";
    }
}
