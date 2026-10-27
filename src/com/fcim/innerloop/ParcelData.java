package com.fcim.innerloop;

import android.content.res.AssetManager;
import android.graphics.Path;
import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

final class ParcelData {
    static final class Feature {
        final int kind, priority;
        final boolean picked;
        final float area, minX, minY, maxX, maxY;
        final String address, siteId, accounts, neighborhood, status;
        final Path path;

        Feature(int kind, int priority, boolean picked, float area,
                float minX, float minY, float maxX, float maxY,
                String address, String siteId, String accounts, String neighborhood, String status, Path path) {
            this.kind = kind;
            this.priority = priority;
            this.picked = picked;
            this.area = area;
            this.minX = minX;
            this.minY = minY;
            this.maxX = maxX;
            this.maxY = maxY;
            this.address = address;
            this.siteId = siteId;
            this.accounts = accounts;
            this.neighborhood = neighborhood;
            this.status = status;
            this.path = path;
        }

        boolean intersects(float left, float bottom, float right, float top) {
            return maxX >= left && minX <= right && maxY >= bottom && minY <= top;
        }
    }

    final List<Feature> features;
    final double originLon, originLat;

    private ParcelData(List<Feature> features, double originLon, double originLat) {
        this.features = features;
        this.originLon = originLon;
        this.originLat = originLat;
    }

    static ParcelData load(AssetManager assets) throws IOException {
        DataInputStream in = new DataInputStream(new BufferedInputStream(assets.open("drive/parcels.bin"), 256 * 1024));
        try {
            if (in.readInt() != 0x494c5033) throw new IOException("Rebuild parcels.bin with stable IDs (ILP3)");
            int count = in.readInt();
            double originLon = in.readDouble();
            double originLat = in.readDouble();
            ArrayList<Feature> result = new ArrayList<>(count);
            for (int i = 0; i < count; i++) {
                int kind = in.readUnsignedByte();
                int priority = in.readUnsignedByte();
                boolean picked = in.readUnsignedByte() != 0;
                in.readUnsignedByte();
                float area = in.readFloat();
                float minX = in.readFloat(), minY = in.readFloat();
                float maxX = in.readFloat(), maxY = in.readFloat();
                int stringLength = in.readInt();
                byte[] raw = new byte[stringLength];
                in.readFully(raw);
                String address = new String(raw, "UTF-8");
                String siteId=readString(in), accounts=readString(in), neighborhood=readString(in), status=readString(in);
                int ringCount = in.readInt();
                Path path = new Path();
                path.setFillType(Path.FillType.EVEN_ODD);
                for (int ring = 0; ring < ringCount; ring++) {
                    int pointCount = in.readInt();
                    for (int point = 0; point < pointCount; point++) {
                        float x = in.readFloat(), y = in.readFloat();
                        if (point == 0) path.moveTo(x, y); else path.lineTo(x, y);
                    }
                    path.close();
                }
                result.add(new Feature(kind, priority, picked, area,
                        minX, minY, maxX, maxY, address, siteId, accounts, neighborhood, status, path));
            }
            return new ParcelData(result, originLon, originLat);
        } finally {
            in.close();
        }
    }

    private static String readString(DataInputStream in) throws IOException {
        int size=in.readInt();
        if(size<0 || size>1024*1024) throw new IOException("Invalid parcel string size");
        byte[] bytes=new byte[size];in.readFully(bytes);return new String(bytes,"UTF-8");
    }
}
