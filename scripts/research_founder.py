#!/usr/bin/env python3
"""Research a founder from Wikipedia and save to Supabase.

Usage: python3 research_founder.py "Steve Jobs" "https://en.wikipedia.org/wiki/Steve_Jobs"

Fetches Wikipedia page, extracts career info via LLM, saves to Supabase.
Returns JSON founder object to stdout.
"""
import json
import os
import sys
import urllib.request
import urllib.parse

# Supabase config
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://tnmbxxcdabecqknzxuus.supabase.co')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

def fetch_wikipedia(title):
    """Fetch full Wikipedia extract for a person."""
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
    """Use OpenClaw gateway to extract career data from Wikipedia text."""
    # Use the gateway's chat API
    gateway_url = 'http://127.0.0.1:18789'
    token = os.environ.get('OPENCLAW_GATEWAY_TOKEN', '')
    
    prompt = f"""Extract the career history of {name} from this Wikipedia text. Return ONLY valid JSON, no markdown, no explanation.

Format:
{{
  "name": "Full Name",
  "roles": [
    {{"company": "Company Name", "role": "Title", "sector": "Specific Sector", "start": YYYY, "end": YYYY_or_null, "note": "optional context"}}
  ],
  "sectorSwitches": [
    {{"from": "Broad Sector", "to": "Broad Sector", "year": YYYY}}
  ],
  "primarySector": "One of: AI, Crypto, Fintech, Social & Media, Consumer, Enterprise, Defense, Deep Tech, VC & Finance, Other"
}}

Rules:
- Include ALL significant roles/companies (not just current)
- end=null means current/ongoing
- Sector should be specific (e.g. "Consumer Electronics" not just "Consumer")
- sectorSwitches only for moves between BROAD sectors: AI, Crypto, Fintech, Social & Media, Consumer, Enterprise, Defense, Deep Tech, VC & Finance, Other
- primarySector = what they're MOST known for
- Sort roles chronologically by start year
- If someone died, their last role should have an end year

Wikipedia text (first 4000 chars):
{wiki_text[:4000]}"""

    payload = {
        "model": "anthropic/claude-sonnet-4-5",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0,
    }
    
    req_data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{gateway_url}/v1/chat/completions",
        data=req_data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
    )
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read().decode())
    content = result['choices'][0]['message']['content']
    
    # Parse JSON from response (handle markdown code blocks)
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[1] if '\n' in content else content[3:]
        content = content.rsplit('```', 1)[0]
    
    return json.loads(content)

def save_to_supabase(founder_data):
    """Save founder + roles + switches to Supabase."""
    if not SUPABASE_SERVICE_KEY:
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
            'company': role['company'],
            'role': role['role'],
            'sector': role['sector'],
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
            print(f"Warning: role insert error: {e}", file=sys.stderr)
    
    # Insert sector switches
    for switch in founder_data.get('sectorSwitches', []):
        switch_row = {
            'founder_id': fid,
            'from_sector': switch['from'],
            'to_sector': switch['to'],
            'year': switch['year'],
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
            print(f"Warning: switch insert error: {e}", file=sys.stderr)
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: research_founder.py 'Name' ['wiki_url']", file=sys.stderr)
        sys.exit(1)
    
    name = sys.argv[1]
    wiki_title = sys.argv[2] if len(sys.argv) > 2 else name
    
    # Fetch Wikipedia
    print(f"Fetching Wikipedia for: {wiki_title}", file=sys.stderr)
    wiki_text, resolved_title = fetch_wikipedia(wiki_title)
    
    if not wiki_text:
        print(f"No Wikipedia article found for: {wiki_title}", file=sys.stderr)
        sys.exit(1)
    
    # Extract career via LLM
    print(f"Extracting career data via LLM...", file=sys.stderr)
    career_data = call_llm(wiki_text, name)
    
    # Build full founder object
    clean_name = resolved_title.split('(')[0].strip()
    founder = {
        'name': career_data.get('name', clean_name),
        'id': clean_name.lower().replace(' ', '-').replace('.', ''),
        'source': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(wiki_title.replace(' ', '_'))}",
        'roles': career_data.get('roles', []),
        'sectorSwitches': career_data.get('sectorSwitches', []),
        'primarySector': career_data.get('primarySector', 'Other'),
        'verified': None,
    }
    
    # Save to Supabase
    if SUPABASE_SERVICE_KEY:
        print(f"Saving to Supabase...", file=sys.stderr)
        save_to_supabase(founder)
    
    # Output JSON to stdout
    print(json.dumps(founder))

if __name__ == '__main__':
    main()
