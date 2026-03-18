#!/usr/bin/env python3
"""Research a founder from Wikipedia via LLM and save to Supabase.

Usage: python3 research_founder.py "Wikipedia Title"

Fetches Wikipedia page, sends to Kimi K2.5 (free via NVIDIA NIM) to extract
career info, saves to Supabase. Returns JSON founder object to stdout.
"""
import json
import os
import re
import sys
import urllib.request
import urllib.parse

# Config
NIM_BASE = "https://integrate.api.nvidia.com/v1"
NIM_MODEL = "moonshotai/kimi-k2.5"
NIM_KEY = os.environ.get('NIM_API_KEY', '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')

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://tnmbxxcdabecqknzxuus.supabase.co')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')


def fetch_wikipedia(title):
    """Fetch Wikipedia intro extract for a person."""
    api_url = (
        f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}"
        f"&prop=extracts&exintro=0&explaintext=1&exsectionformat=plain&format=json"
    )
    req = urllib.request.Request(api_url, headers={'User-Agent': 'WhereNext/1.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    pages = data.get('query', {}).get('pages', {})
    page = list(pages.values())[0] if pages else {}
    return page.get('extract', ''), page.get('title', title)


def call_llm(wiki_text, name):
    """Use Kimi K2.5 via NVIDIA NIM to extract career data."""
    prompt = f"""Extract the career history of {name} from this Wikipedia text. Return ONLY valid JSON, no markdown, no explanation.

Format:
{{"name":"Full Name","roles":[{{"company":"Company Name","role":"Title","sector":"Specific Sector","start":YYYY,"end":YYYY_or_null,"note":"optional brief context"}}],"sectorSwitches":[{{"from":"Broad Sector","to":"Broad Sector","year":YYYY}}],"primarySector":"One of: AI, Crypto, Fintech, Social & Media, Consumer, Enterprise, Defense, Deep Tech, VC & Finance, Other"}}

Rules:
- Include ALL significant companies/roles, not just current
- end=null means current/ongoing. If person died, last roles end at death year
- Sector should be specific (e.g. "Consumer Electronics" not just "Consumer")  
- sectorSwitches only for moves between BROAD sectors: AI, Crypto, Fintech, Social & Media, Consumer, Enterprise, Defense, Deep Tech, VC & Finance, Other
- primarySector = what they're MOST known for
- Sort roles chronologically by start year
- Max 8 roles (most important ones)

Wikipedia text (first 3000 chars):
{wiki_text[:3000]}"""

    payload = json.dumps({
        "model": NIM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0,
    }).encode()

    req = urllib.request.Request(
        f"{NIM_BASE}/chat/completions",
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {NIM_KEY}',
        }
    )
    resp = urllib.request.urlopen(req, timeout=120)
    result = json.loads(resp.read().decode())
    
    choice = result['choices'][0]
    content = choice['message'].get('content') or ''
    
    # Strip markdown code blocks if present
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[1] if '\n' in content else content[3:]
        content = content.rsplit('```', 1)[0]
    content = content.strip()
    
    return json.loads(content)


def save_to_supabase(founder_data):
    """Save founder + roles to Supabase."""
    if not SUPABASE_SERVICE_KEY:
        print("No SUPABASE_SERVICE_KEY, skipping DB save", file=sys.stderr)
        return False

    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates',
    }
    base = f"{SUPABASE_URL}/rest/v1"
    fid = founder_data['id']

    # Upsert founder
    founder_row = {
        'id': fid,
        'name': founder_data['name'],
        'primary_sector': founder_data.get('primarySector', 'Other'),
        'source_url': founder_data.get('source', ''),
        'verified': None,
    }
    req = urllib.request.Request(
        f"{base}/founders",
        data=json.dumps(founder_row).encode(),
        headers={**headers, 'Prefer': 'resolution=merge-duplicates'},
        method='POST'
    )
    urllib.request.urlopen(req, timeout=10)

    # Insert roles
    for i, role in enumerate(founder_data.get('roles', [])):
        role_row = {
            'founder_id': fid,
            'company': role.get('company', ''),
            'role': role.get('role', ''),
            'sector': role.get('sector', 'Other'),
            'start_year': role.get('start'),
            'end_year': role.get('end'),
            'note': role.get('note'),
            'sort_order': i,
        }
        req = urllib.request.Request(
            f"{base}/roles",
            data=json.dumps(role_row).encode(),
            headers=headers,
            method='POST'
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f"Warning: role insert: {e}", file=sys.stderr)

    # Insert sector switches
    for switch in founder_data.get('sectorSwitches', []):
        switch_row = {
            'founder_id': fid,
            'from_sector': switch.get('from', ''),
            'to_sector': switch.get('to', ''),
            'year': switch.get('year'),
        }
        req = urllib.request.Request(
            f"{base}/sector_switches",
            data=json.dumps(switch_row).encode(),
            headers=headers,
            method='POST'
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f"Warning: switch insert: {e}", file=sys.stderr)

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: research_founder.py 'Wikipedia Title'", file=sys.stderr)
        sys.exit(1)

    title = sys.argv[1]

    # Fetch Wikipedia
    print(f"Fetching Wikipedia: {title}", file=sys.stderr)
    wiki_text, resolved_title = fetch_wikipedia(title)
    if not wiki_text:
        print(json.dumps({'error': f'No Wikipedia article: {title}'}))
        sys.exit(1)

    # Extract career via LLM
    print(f"Extracting career via {NIM_MODEL}...", file=sys.stderr)
    career = call_llm(wiki_text, resolved_title.split('(')[0].strip())

    # Build founder object — use search title for ID (matches frontend expectation)
    search_name = title.split('(')[0].strip()
    clean_name = career.get('name', search_name)
    # ID from search name so frontend polling matches
    fid = re.sub(r'[^a-z0-9]+', '-', search_name.lower()).strip('-')

    founder = {
        'name': clean_name,
        'id': fid,
        'source': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
        'roles': career.get('roles', []),
        'sectorSwitches': career.get('sectorSwitches', []),
        'primarySector': career.get('primarySector', 'Other'),
        'verified': None,
    }

    # Save to Supabase
    saved = save_to_supabase(founder)
    print(f"Supabase: {'saved' if saved else 'skipped'}", file=sys.stderr)

    # Output JSON
    print(json.dumps(founder))


if __name__ == '__main__':
    main()
