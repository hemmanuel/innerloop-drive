"""Stable identities shared by screening snapshots, imports and the native bundle."""
import hashlib
import re


def accounts(value):
    parts = re.split(r'[\s,;]+', value.strip()) if isinstance(value,str) else value
    result = sorted(set(str(p).strip() for p in parts if str(p).strip()))
    if not result or any(not re.fullmatch(r'\d{13}',p) for p in result):
        raise ValueError('HCAD accounts must be 13-digit strings (preserve leading zeros)')
    return result


def site_id(value):
    members=accounts(value)
    return 'S'+members[0] if len(members)==1 else 'A'+hashlib.sha256('|'.join(members).encode()).hexdigest()[:24]
