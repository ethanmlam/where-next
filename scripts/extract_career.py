#!/usr/bin/env python3
"""Extract career data from a Wikipedia article. No LLM needed.

Uses Wikipedia's structured data (infobox) + text parsing.
Returns JSON to stdout.
"""
import json
import re
import sys
import urllib.request
import urllib.parse


def fetch_wiki_page(title):
    """Fetch Wikipedia page with both HTML and plaintext."""
    # Get plaintext extract
    api_url = (
        f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}"
        f"&prop=extracts|revisions&explaintext=1&exsectionformat=plain"
        f"&rvprop=content&rvslots=main&format=json"
    )
    req = urllib.request.Request(api_url, headers={'User-Agent': 'WhereNext/1.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode())
    pages = data.get('query', {}).get('pages', {})
    page = list(pages.values())[0] if pages else {}
    extract = page.get('extract', '')
    
    # Get wikitext for infobox parsing
    wikitext = ''
    revisions = page.get('revisions', [])
    if revisions:
        wikitext = revisions[0].get('slots', {}).get('main', {}).get('*', '')
    
    return extract, wikitext, page.get('title', title)


def parse_infobox(wikitext):
    """Extract structured data from the infobox."""
    info = {}
    # Find the infobox
    match = re.search(r'\{\{Infobox\s+[^|]*\|(.+?)(?:\n\}\}|\n\|)', wikitext, re.DOTALL | re.IGNORECASE)
    if not match:
        return info
    
    # Get all infobox content between {{ and }}
    depth = 0
    start = wikitext.find('{{Infobox')
    if start == -1:
        start = wikitext.find('{{infobox')
    if start == -1:
        return info
    
    pos = start + 2
    while pos < len(wikitext):
        if wikitext[pos:pos+2] == '{{':
            depth += 1
            pos += 2
        elif wikitext[pos:pos+2] == '}}':
            if depth == 0:
                infobox_text = wikitext[start+2:pos]
                break
            depth -= 1
            pos += 2
        else:
            pos += 1
    else:
        return info
    
    # Parse key-value pairs
    for line in infobox_text.split('\n'):
        line = line.strip()
        if line.startswith('|') and '=' in line:
            key, _, value = line[1:].partition('=')
            key = key.strip().lower()
            value = re.sub(r'\[\[([^|\]]*\|)?([^\]]*)\]\]', r'\2', value.strip())  # Remove wiki links
            value = re.sub(r'\{\{[^}]*\}\}', '', value)  # Remove templates
            value = re.sub(r'<[^>]*>', '', value)  # Remove HTML
            value = value.strip()
            if value:
                info[key] = value
    
    return info


def extract_career(extract, wikitext, name):
    """Extract career roles from Wikipedia text."""
    infobox = parse_infobox(wikitext)
    roles = []
    seen = set()
    
    # Get birth/death years
    birth_year = None
    death_year = None
    birth_match = re.search(r'born[^)]*?(\d{4})', extract[:500])
    if birth_match:
        birth_year = int(birth_match.group(1))
    death_match = re.search(r'(\d{4})\s*[)–\-]\s*(?:died|was|$)', extract[:500])
    if not death_match:
        death_match = re.search(r'–\s*(?:\w+\s+\d{1,2},?\s+)?(\d{4})\)', extract[:500])
    if death_match:
        death_year = int(death_match.group(1))
    
    # Pattern: "founded/co-founded COMPANY in YEAR"
    for m in re.finditer(r'(?:co-?)?found(?:ed|er\s+(?:of|and\s+\w+\s+of))\s+([A-Z][A-Za-z0-9\s&.\-\']+?)(?:\s+in\s+(\d{4})|[,.])', extract):
        company = m.group(1).strip().rstrip('.,;:')
        for junk in [' and ', ' in ', ' with ', ' the same', ' where']:
            if junk in company.lower():
                company = company[:company.lower().index(junk)]
        company = company.strip().rstrip('.,;:')
        year = int(m.group(2)) if m.group(2) else None
        if 2 < len(company) < 35 and company.lower() not in seen:
            seen.add(company.lower())
            roles.append({'company': company, 'role': 'Co-founder' if 'co-' in m.group(0).lower() else 'Founder', 'start': year})
    
    # Pattern: "CEO/CTO/President of COMPANY"
    for m in re.finditer(r'(CEO|CTO|COO|chairman|president|chief\s+\w+\s+officer)\s+(?:of\s+)?([A-Z][A-Za-z0-9\s&.\-\']+?)(?:\s+(?:from|since|in|starting)\s+(\d{4})|[,.])', extract, re.IGNORECASE):
        role_title = m.group(1).strip()
        company = m.group(2).strip().rstrip('.,;:')
        for junk in [' and ', ' in ', ' from ', ' with ', ' where']:
            if junk in company.lower():
                company = company[:company.lower().index(junk)]
        company = company.strip().rstrip('.,;:')
        year = int(m.group(3)) if m.group(3) else None
        if 2 < len(company) < 35 and company.lower() not in seen:
            seen.add(company.lower())
            roles.append({'company': company, 'role': role_title.title(), 'start': year})
    
    # Pattern: "joined COMPANY in YEAR" or "worked at COMPANY"
    for m in re.finditer(r'(?:joined|worked\s+(?:at|for))\s+([A-Z][A-Za-z0-9\s&.\-\']+?)(?:\s+in\s+(\d{4})|[,.])', extract):
        company = m.group(1).strip().rstrip('.,;:')
        for junk in [' and ', ' in ', ' from ', ' as ', ' where']:
            if junk in company.lower():
                company = company[:company.lower().index(junk)]
        company = company.strip().rstrip('.,;:')
        year = int(m.group(2)) if m.group(2) else None
        if 2 < len(company) < 35 and company.lower() not in seen:
            seen.add(company.lower())
            roles.append({'company': company, 'role': 'Executive', 'start': year})
    
    # Try to get role info from infobox
    if not roles:
        for key in ['occupation', 'known_for', 'title']:
            if key in infobox:
                # Try to extract company names from these fields
                for m in re.finditer(r'([A-Z][A-Za-z0-9\s&.\-]+)', infobox[key]):
                    company = m.group(1).strip()
                    if 3 < len(company) < 30 and company.lower() not in seen:
                        seen.add(company.lower())
                        roles.append({'company': company, 'role': 'Founder', 'start': None})
    
    # Sort by start year
    roles.sort(key=lambda r: r.get('start') or 9999)
    
    # Add sector guesses and end years
    sector_map = {
        'apple': 'Consumer Electronics', 'google': 'Enterprise', 'meta': 'Social Media',
        'facebook': 'Social Media', 'amazon': 'Consumer Tech', 'microsoft': 'Enterprise',
        'tesla': 'Automotive / Clean Energy', 'spacex': 'Commercial Space',
        'twitter': 'Social Media', 'netflix': 'Consumer', 'uber': 'Consumer',
        'airbnb': 'Consumer', 'stripe': 'Fintech', 'paypal': 'Fintech',
        'openai': 'AI', 'anthropic': 'AI Safety', 'deepmind': 'AI Research',
        'palantir': 'Defense Tech', 'coinbase': 'Crypto', 'nvidia': 'Semiconductors / AI',
        'salesforce': 'Enterprise SaaS', 'oracle': 'Enterprise', 'ibm': 'Enterprise',
        'intel': 'Semiconductors', 'amd': 'Semiconductors', 'cisco': 'Enterprise',
        'linkedin': 'Professional Social Network', 'snap': 'Social Media',
        'pinterest': 'Social Media', 'slack': 'Enterprise SaaS', 'zoom': 'Enterprise',
        'shopify': 'E-commerce', 'square': 'Fintech', 'block': 'Fintech',
        'robinhood': 'Fintech', 'figma': 'Enterprise', 'github': 'Developer Tools',
        'youtube': 'Social Media', 'instagram': 'Social Media', 'whatsapp': 'Social Media',
        'pixar': 'Entertainment', 'next': 'Enterprise', 'nest': 'Consumer Electronics / IoT',
    }
    
    for role in roles:
        c_lower = role['company'].lower()
        role['sector'] = 'Other'
        for pattern, sector in sector_map.items():
            if pattern in c_lower:
                role['sector'] = sector
                break
        role['end'] = None
        if death_year and role.get('start') and role['start'] < death_year:
            role['end'] = death_year
    
    # Build full entry
    clean_name = name.split('(')[0].strip()
    
    # Guess primary sector from most recent role
    primary = 'Other'
    if roles:
        last_sector = roles[-1].get('sector', 'Other')
        # Map to broad sector
        broad_map = {
            'ai': 'AI', 'ml': 'AI', 'artificial': 'AI',
            'crypto': 'Crypto', 'blockchain': 'Crypto',
            'fintech': 'Fintech', 'payment': 'Fintech', 'finance': 'Fintech',
            'social': 'Social & Media', 'media': 'Social & Media',
            'consumer': 'Consumer', 'e-commerce': 'Consumer', 'entertainment': 'Consumer',
            'enterprise': 'Enterprise', 'saas': 'Enterprise', 'developer': 'Enterprise',
            'defense': 'Defense', 'military': 'Defense',
            'semiconductor': 'Deep Tech', 'space': 'Deep Tech', 'automotive': 'Deep Tech',
            'biotech': 'Deep Tech', 'energy': 'Deep Tech', 'iot': 'Deep Tech',
            'vc': 'VC & Finance', 'venture': 'VC & Finance', 'invest': 'VC & Finance',
        }
        ls = last_sector.lower()
        for pattern, broad in broad_map.items():
            if pattern in ls:
                primary = broad
                break
    
    return {
        'name': clean_name,
        'id': re.sub(r'[^a-z0-9]+', '-', clean_name.lower()).strip('-'),
        'source': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(name.replace(' ', '_'))}",
        'roles': [{'company': r['company'], 'role': r['role'], 'sector': r['sector'],
                    'start': r.get('start'), 'end': r.get('end')} for r in roles[:8]],
        'sectorSwitches': [],
        'primarySector': primary,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_career.py 'Wikipedia Title'", file=sys.stderr)
        sys.exit(1)
    
    title = sys.argv[1]
    extract, wikitext, resolved = fetch_wiki_page(title)
    
    if not extract:
        print(json.dumps({'error': f'No article found for {title}'}))
        sys.exit(1)
    
    result = extract_career(extract, wikitext, resolved)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
