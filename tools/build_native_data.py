#!/usr/bin/env python3
"""Convert generated Inner Loop JavaScript datasets to a compact native binary.

The binary contains every context and candidate parcel, but only fields needed by
Drive. Coordinates are local Web Mercator metres so Android can draw them without
JSON parsing or per-frame geographic projection.
"""
import json
import math
import os
import struct
import sys
import gzip
from site_identity import site_id, accounts as account_list

R = 6378137.0
ORIGIN_LON = -95.36
ORIGIN_LAT = 29.75
OX = R * math.radians(ORIGIN_LON)
OY = R * math.log(math.tan(math.pi / 4 + math.radians(ORIGIN_LAT) / 2))


def load_js(path, prefix):
    text = open(path, encoding="utf-8").read().strip()
    if not text.startswith(prefix):
        raise SystemExit(f"Unexpected data wrapper in {path}")
    return json.loads(text[len(prefix):].rstrip(";"))


def xy(point):
    lon, lat = point
    x = R * math.radians(lon) - OX
    y = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) - OY
    return x, y


def text(out, value):
    raw = str(value or "").encode("utf-8")
    out.write(struct.pack(">I", len(raw)))
    out.write(raw)


def feature(out, kind, priority, picked, area, address, geom, identity, accounts, neighborhood='', status='legacy'):
    rings = [ring for ring in geom if len(ring) >= 3]
    points = [xy(p) for ring in rings for p in ring]
    if not points:
        return False
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    out.write(struct.pack(">BBBBfffff", kind, priority, int(picked), 0,
                          float(area or 0), min(xs), min(ys), max(xs), max(ys)))
    text(out, address)
    text(out, identity)
    text(out, ' '.join(accounts))
    text(out, neighborhood)
    text(out, status)
    out.write(struct.pack(">I", len(rings)))
    for ring in rings:
        out.write(struct.pack(">I", len(ring)))
        for point in ring:
            out.write(struct.pack(">ff", *xy(point)))
    return True


def main(source, destination):
    if os.path.isfile(source) and source.endswith('.jsonl.gz'):
        return snapshot(source,destination)
    parcels = load_js(os.path.join(source, "parcels.js"), "window.PARCELS = ")
    lots = load_js(os.path.join(source, "data.js"), "window.LOTDATA = ")
    picks_path = os.path.join(source, "picks.js")
    picks = set()
    if os.path.exists(picks_path):
        raw = open(picks_path, encoding="utf-8").read()
        start, end = raw.find("["), raw.rfind("]")
        if start >= 0 and end > start:
            picks.update(json.loads(raw[start:end + 1]))

    pc = {name: i for i, name in enumerate(parcels["cols"])}
    lc = {name: i for i, name in enumerate(lots["cols"])}
    count = len(parcels["geoms"]) + len(lots["geoms"])
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, "wb") as out:
        out.write(b"ILP3")
        out.write(struct.pack(">Idd", count, ORIGIN_LON, ORIGIN_LAT))
        written = 0
        for row, geom in zip(parcels["rows"], parcels["geoms"]):
            members=account_list(str(row[pc['acct']]))
            written += feature(out, 0, 0, False, row[pc["sf"]], row[pc["addr"]], geom,
                               site_id(members),members,str(row[pc['area']]))
        priority_code = {"X": 0, "C": 1, "B": 2, "A": 3}
        for row, geom in zip(lots["rows"], lots["geoms"]):
            accounts = str(row[lc["accts"]] or "")
            members=account_list(accounts)
            written += feature(out, 1, priority_code.get(row[lc["priority"]], 0),
                               accounts in picks, row[lc["land_ar"]],
                               row[lc["addresses"]], geom,site_id(members),members,str(row[lc['area']]))
        if written != count:
            raise SystemExit(f"Expected {count} features, wrote {written}")
    print(f"Wrote {count:,} parcels to {destination} ({os.path.getsize(destination)/1048576:.1f} MiB)")


def snapshot(source,destination):
    """The exact same snapshot is consumed by Supabase and offline Drive."""
    os.makedirs(os.path.dirname(os.path.abspath(destination)),exist_ok=True)
    count=0
    with open(destination,'wb') as out:
        out.write(b'ILP3');out.write(struct.pack('>Idd',0,ORIGIN_LON,ORIGIN_LAT))
        with gzip.open(source,'rt',encoding='utf-8') as inp:
            for line in inp:
                row=json.loads(line);g=row['geometry']
                if g is None:continue
                rings=g['coordinates'] if g['type']=='Polygon' else [ring for poly in g['coordinates'] for ring in poly]
                count+=feature(out,1 if row['area_sf']>=10000 else 0,3 if row['fits'] else 0,False,
                  row['area_sf'],row['address'],rings,row['site_id'],row['accounts'],row['neighborhood'],row['status'])
        out.seek(4);out.write(struct.pack('>I',count))
    print(f'Wrote {count:,} mapped sites with stable IDs to {destination}')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_native_data.py SOURCE_DIR OUTPUT_FILE")
    main(sys.argv[1], sys.argv[2])
