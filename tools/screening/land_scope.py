"""Distinguish an independently assessed land site from a condominium interest."""
import math
import re


def reported_area(row):
    value=row.get('area_sf')
    return float(value) if value is not None and math.isfinite(value) and value>0 else 0.0


def scope_issue(row):
    legal=str(row.get('legal_text') or '').upper()
    condo=bool(re.search(r'\bCONDO(?:MINIUM)?S?\b',legal) or
               re.search(r'\bINT\b.*\bCOMMON\s+(?:LAND|ELEMENT)',legal))
    if condo:return {'fits':False,'status':'condominium_interest','reason':'Condominium/common-land interest; not exclusive control of the mapped parcel'}
    if row.get('shared_geometry_accounts',1)>1:
        return {'fits':False,'status':'shared_geometry_review','reason':'Multiple tax accounts use the same parcel boundary'}
    if reported_area(row)==0:
        return {'fits':False,'status':'land_area_review','reason':'No positive recorded land area; parcel polygon area is retained separately'}
    return None
