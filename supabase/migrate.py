#!/usr/bin/env python3
# NOTE: Supabase is now the source of truth. This script is for historical reference
# and can be used to re-seed the database if needed. founders.json has been removed.
"""Migrate founders.json -> Supabase"""
import json
import os
import sys

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase-py...")
    os.system(f"{sys.executable} -m pip install supabase")
    from supabase import create_client

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')  # Use service role key for migration

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Set SUPABASE_URL and SUPABASE_SERVICE_KEY env vars")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load founders
data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'founders.json')
with open(data_file) as f:
    founders = json.load(f)

print(f"Migrating {len(founders)} founders...")

for founder in founders:
    fid = founder['id']
    
    # Insert founder
    founder_row = {
        'id': fid,
        'name': founder['name'],
        'primary_sector': founder.get('primarySector', 'Other'),
        'source_url': founder.get('source', ''),
        'verified': founder.get('verified'),
    }
    
    try:
        supabase.table('founders').upsert(founder_row).execute()
    except Exception as e:
        print(f"  Error inserting founder {fid}: {e}")
        continue
    
    # Delete existing roles & switches before re-inserting
    try:
        supabase.table('roles').delete().eq('founder_id', fid).execute()
        supabase.table('sector_switches').delete().eq('founder_id', fid).execute()
    except Exception as e:
        print(f"  Error clearing old data for {fid}: {e}")

    # Insert roles
    for i, role in enumerate(founder.get('roles', [])):
        role_row = {
            'founder_id': fid,
            'company': role['company'],
            'role': role['role'],
            'sector': role['sector'],
            'start_year': role.get('start'),
            'end_year': role.get('end'),
            'note': role.get('note'),
            'sort_order': i,
        }
        try:
            supabase.table('roles').insert(role_row).execute()
        except Exception as e:
            print(f"  Error inserting role for {fid}: {e}")
    
    # Insert sector switches
    for switch in founder.get('sectorSwitches', []):
        switch_row = {
            'founder_id': fid,
            'from_sector': switch['from'],
            'to_sector': switch['to'],
            'year': switch['year'],
        }
        try:
            supabase.table('sector_switches').insert(switch_row).execute()
        except Exception as e:
            print(f"  Error inserting switch for {fid}: {e}")
    
    print(f"  + {founder['name']} ({len(founder.get('roles', []))} roles, {len(founder.get('sectorSwitches', []))} switches)")

print(f"\nDone! {len(founders)} founders migrated.")
