#!/usr/bin/env python3
"""Insert 23 new founders to reach 300 total in Supabase."""
import json
import os
import sys
import urllib.request

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://tnmbxxcdabecqknzxuus.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_KEY:
    print("Set SUPABASE_SERVICE_KEY env var")
    sys.exit(1)

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'resolution=merge-duplicates',
}
BASE = f"{SUPABASE_URL}/rest/v1"

FOUNDERS = [
    {
        "name": "Russel Simmons",
        "id": "russel-simmons",
        "primarySector": "Consumer",
        "source": "https://en.wikipedia.org/wiki/Russel_Simmons_(entrepreneur)",
        "roles": [
            {"company": "PayPal", "role": "Software Engineer", "sector": "Fintech", "start": 2000, "end": 2004, "note": "Early engineer"},
            {"company": "Yelp", "role": "Co-founder & CTO", "sector": "Consumer Tech", "start": 2004, "end": 2010, "note": "Co-founded with Jeremy Stoppelman"},
            {"company": "Angel Investing", "role": "Angel Investor", "sector": "VC", "start": 2010, "end": None, "note": None}
        ],
        "sectorSwitches": [
            {"from": "Fintech", "to": "Consumer", "year": 2004},
            {"from": "Consumer", "to": "VC & Finance", "year": 2010}
        ]
    },
    {
        "name": "Dave McClure",
        "id": "dave-mcclure",
        "primarySector": "VC & Finance",
        "source": "https://en.wikipedia.org/wiki/Dave_McClure_(investor)",
        "roles": [
            {"company": "PayPal", "role": "Director of Marketing", "sector": "Fintech", "start": 1999, "end": 2004, "note": None},
            {"company": "500 Startups", "role": "Founder & GP", "sector": "VC", "start": 2010, "end": 2017, "note": "Prolific seed investor, 2000+ investments"},
            {"company": "Practical VC", "role": "Founder", "sector": "VC", "start": 2018, "end": None, "note": None}
        ],
        "sectorSwitches": [
            {"from": "Fintech", "to": "VC & Finance", "year": 2010}
        ]
    },
    {
        "name": "Joe Gebbia",
        "id": "joe-gebbia",
        "primarySector": "Consumer",
        "source": "https://en.wikipedia.org/wiki/Joe_Gebbia",
        "roles": [
            {"company": "Airbnb", "role": "Co-founder & CPO", "sector": "Consumer Tech", "start": 2008, "end": 2022, "note": "YC W09"},
            {"company": "Airbnb", "role": "Chairman of Samara", "sector": "Consumer Tech", "start": 2022, "end": 2023, "note": "Internal design studio"},
            {"company": "Venture & Design", "role": "Independent", "sector": "VC", "start": 2023, "end": None, "note": None}
        ],
        "sectorSwitches": [
            {"from": "Consumer", "to": "VC & Finance", "year": 2023}
        ]
    },
    {
        "name": "Nathan Blecharczyk",
        "id": "nathan-blecharczyk",
        "primarySector": "Consumer",
        "source": "https://en.wikipedia.org/wiki/Nathan_Blecharczyk",
        "roles": [
            {"company": "Airbnb", "role": "Co-founder & Chief Strategy Officer", "sector": "Consumer Tech", "start": 2008, "end": None, "note": "YC W09, built original platform"}
        ],
        "sectorSwitches": []
    },
    {
        "name": "Tracy Young",
        "id": "tracy-young",
        "primarySector": "Enterprise",
        "source": "https://en.wikipedia.org/wiki/Tracy_Young_(entrepreneur)",
        "roles": [
            {"company": "PlanGrid", "role": "Co-founder & CEO", "sector": "Enterprise SaaS", "start": 2012, "end": 2019, "note": "YC W12, construction tech"},
            {"company": "Autodesk", "role": "VP", "sector": "Enterprise", "start": 2019, "end": 2020, "note": "Acquired PlanGrid for $875M"},
            {"company": "TigerEye", "role": "Co-founder & CEO", "sector": "Enterprise SaaS", "start": 2020, "end": None, "note": "CRM analytics"}
        ],
        "sectorSwitches": []
    },
    {
        "name": "Mathilde Collin",
        "id": "mathilde-collin",
        "primarySector": "Enterprise",
        "source": "https://en.wikipedia.org/wiki/Mathilde_Collin",
        "roles": [
            {"company": "Front", "role": "Co-founder & CEO", "sector": "Enterprise SaaS", "start": 2014, "end": None, "note": "YC S14, shared inbox platform"}
        ],
        "sectorSwitches": []
    },
    {
        "name": "Calvin French-Owen",
        "id": "calvin-french-owen",
        "primarySector": "Enterprise",
        "source": "https://en.wikipedia.org/wiki/Segment_(company)",
        "roles": [
            {"company": "Segment", "role": "Co-founder & CTO", "sector": "Enterprise SaaS", "start": 2011, "end": 2020, "note": "YC S11, customer data platform"},
            {"company": "Twilio", "role": "VP Engineering", "sector": "Enterprise", "start": 2020, "end": 2022, "note": "Acquired Segment for $3.2B"},
            {"company": "Vessel", "role": "Co-founder", "sector": "AI", "start": 2023, "end": None, "note": "AI startup"}
        ],
        "sectorSwitches": [
            {"from": "Enterprise", "to": "AI", "year": 2023}
        ]
    },
    {
        "name": "Austen Allred",
        "id": "austen-allred",
        "primarySector": "Consumer",
        "source": "https://en.wikipedia.org/wiki/Austen_Allred",
        "roles": [
            {"company": "Lambda School", "role": "Founder & CEO", "sector": "Education/Consumer", "start": 2017, "end": 2022, "note": "YC S17, income share agreements"},
            {"company": "BloomTech", "role": "CEO", "sector": "Education/Consumer", "start": 2022, "end": 2023, "note": "Rebranded Lambda School"},
            {"company": "AI ventures", "role": "Founder", "sector": "AI", "start": 2023, "end": None, "note": "Pivoted to AI training data"}
        ],
        "sectorSwitches": [
            {"from": "Consumer", "to": "AI", "year": 2023}
        ]
    },
    {
        "name": "Yoshua Bengio",
        "id": "yoshua-bengio",
        "primarySector": "AI",
        "source": "https://en.wikipedia.org/wiki/Yoshua_Bengio",
        "roles": [
            {"company": "Université de Montréal", "role": "Professor", "sector": "Academia/AI Research", "start": 1993, "end": None, "note": None},
            {"company": "MILA", "role": "Founder & Scientific Director", "sector": "AI Research", "start": 2003, "end": None, "note": "Quebec AI Institute"},
            {"company": "Element AI", "role": "Co-founder", "sector": "AI", "start": 2016, "end": 2021, "note": "Acquired by ServiceNow"},
            {"company": "Turing Award", "role": "Laureate", "sector": "AI Research", "start": 2018, "end": 2018, "note": "Shared with Hinton & LeCun"}
        ],
        "sectorSwitches": []
    },
    {
        "name": "Liang Wenfeng",
        "id": "liang-wenfeng",
        "primarySector": "AI",
        "source": "https://en.wikipedia.org/wiki/Liang_Wenfeng",
        "roles": [
            {"company": "High-Flyer Capital", "role": "Founder", "sector": "Hedge Fund/Quantitative Trading", "start": 2015, "end": 2023, "note": "Quant hedge fund in Hangzhou"},
            {"company": "DeepSeek", "role": "Founder", "sector": "AI", "start": 2023, "end": None, "note": "Built R1/V3, rivaled frontier US models at fraction of cost"}
        ],
        "sectorSwitches": [
            {"from": "VC & Finance", "to": "AI", "year": 2023}
        ]
    },
    {
        "name": "Cameron Winklevoss",
        "id": "cameron-winklevoss",
        "primarySector": "Crypto",
        "source": "https://en.wikipedia.org/wiki/Cameron_Winklevoss",
        "roles": [
            {"company": "ConnectU", "role": "Co-founder", "sector": "Social Media", "start": 2002, "end": 2008, "note": "Facebook lawsuit, settled $65M"},
            {"company": "Winklevoss Capital", "role": "Co-founder", "sector": "VC", "start": 2012, "end": None, "note": "Early Bitcoin investors, bought BTC at ~$10"},
            {"company": "Gemini", "role": "Co-founder & President", "sector": "Crypto Exchange", "start": 2014, "end": None, "note": "Regulated crypto exchange"}
        ],
        "sectorSwitches": [
            {"from": "Social & Media", "to": "VC & Finance", "year": 2012},
            {"from": "VC & Finance", "to": "Crypto", "year": 2014}
        ]
    },
    {
        "name": "Tyler Winklevoss",
        "id": "tyler-winklevoss",
        "primarySector": "Crypto",
        "source": "https://en.wikipedia.org/wiki/Tyler_Winklevoss",
        "roles": [
            {"company": "ConnectU", "role": "Co-founder", "sector": "Social Media", "start": 2002, "end": 2008, "note": "Facebook lawsuit, settled $65M"},
            {"company": "Winklevoss Capital", "role": "Co-founder", "sector": "VC", "start": 2012, "end": None, "note": "Early Bitcoin investors"},
            {"company": "Gemini", "role": "Co-founder & CEO", "sector": "Crypto Exchange", "start": 2014, "end": None, "note": "Regulated crypto exchange"}
        ],
        "sectorSwitches": [
            {"from": "Social & Media", "to": "VC & Finance", "year": 2012},
            {"from": "VC & Finance", "to": "Crypto", "year": 2014}
        ]
    },
    {
        "name": "Eduardo Saverin",
        "id": "eduardo-saverin",
        "primarySector": "VC & Finance",
        "source": "https://en.wikipedia.org/wiki/Eduardo_Saverin",
        "roles": [
            {"company": "Facebook", "role": "Co-founder & CFO", "sector": "Social Media", "start": 2004, "end": 2005, "note": "Provided initial $19K funding"},
            {"company": "Angel Investing", "role": "Angel Investor", "sector": "VC", "start": 2009, "end": 2015, "note": "Based in Singapore"},
            {"company": "B Capital Group", "role": "Co-founder", "sector": "VC", "start": 2015, "end": None, "note": "Growth-stage VC, SE Asia focus"}
        ],
        "sectorSwitches": [
            {"from": "Social & Media", "to": "VC & Finance", "year": 2009}
        ]
    },
    {
        "name": "Tom Anderson",
        "id": "tom-anderson",
        "primarySector": "Social & Media",
        "source": "https://en.wikipedia.org/wiki/Tom_Anderson",
        "roles": [
            {"company": "Myspace", "role": "Co-founder & President", "sector": "Social Media", "start": 2003, "end": 2009, "note": "Everyone's first friend, sold to News Corp for $580M"},
            {"company": "Photography & Travel", "role": "Retired", "sector": "Other", "start": 2009, "end": None, "note": "Left tech, became travel photographer"}
        ],
        "sectorSwitches": [
            {"from": "Social & Media", "to": "Other", "year": 2009}
        ]
    },
    {
        "name": "Chris Hughes",
        "id": "chris-hughes",
        "primarySector": "Social & Media",
        "source": "https://en.wikipedia.org/wiki/Chris_Hughes",
        "roles": [
            {"company": "Facebook", "role": "Co-founder & Spokesperson", "sector": "Social Media", "start": 2004, "end": 2007, "note": "Facebook co-founder #4"},
            {"company": "Obama Campaign", "role": "Director of Online Organizing", "sector": "Government/Policy", "start": 2007, "end": 2008, "note": "Built my.barackobama.com"},
            {"company": "The New Republic", "role": "Owner & Publisher", "sector": "Media", "start": 2012, "end": 2016, "note": None},
            {"company": "Economic Security Project", "role": "Co-chair", "sector": "Nonprofit", "start": 2016, "end": None, "note": "UBI advocacy"}
        ],
        "sectorSwitches": [
            {"from": "Social & Media", "to": "Other", "year": 2007},
            {"from": "Other", "to": "Social & Media", "year": 2012},
            {"from": "Social & Media", "to": "Other", "year": 2016}
        ]
    },
    {
        "name": "Biz Stone",
        "id": "biz-stone",
        "primarySector": "Social & Media",
        "source": "https://en.wikipedia.org/wiki/Biz_Stone",
        "roles": [
            {"company": "Google", "role": "Blogger Team", "sector": "Enterprise", "start": 2003, "end": 2005, "note": "Worked on Blogger with Ev Williams"},
            {"company": "Twitter", "role": "Co-founder", "sector": "Social Media", "start": 2006, "end": 2011, "note": "Co-founded with Dorsey & Williams"},
            {"company": "Jelly", "role": "Co-founder & CEO", "sector": "Consumer Tech", "start": 2013, "end": 2017, "note": "Q&A app, acquired by Pinterest"},
            {"company": "Twitter", "role": "Advisor", "sector": "Social Media", "start": 2017, "end": 2019, "note": "Returned as senior advisor"},
            {"company": "Medium", "role": "Advisor", "sector": "Media", "start": 2020, "end": None, "note": None}
        ],
        "sectorSwitches": [
            {"from": "Enterprise", "to": "Social & Media", "year": 2006},
            {"from": "Social & Media", "to": "Consumer", "year": 2013},
            {"from": "Consumer", "to": "Social & Media", "year": 2017}
        ]
    },
    {
        "name": "Brandon Tseng",
        "id": "brandon-tseng",
        "primarySector": "Defense",
        "source": "https://en.wikipedia.org/wiki/Shield_AI",
        "roles": [
            {"company": "US Navy", "role": "Navy SEAL Officer", "sector": "Defense", "start": 2008, "end": 2014, "note": "Multiple deployments"},
            {"company": "Shield AI", "role": "Co-founder & President", "sector": "Defense Tech", "start": 2015, "end": None, "note": "Autonomous military drones, valued at $2.7B+"}
        ],
        "sectorSwitches": []
    },
    {
        "name": "Nikesh Arora",
        "id": "nikesh-arora",
        "primarySector": "Enterprise",
        "source": "https://en.wikipedia.org/wiki/Nikesh_Arora",
        "roles": [
            {"company": "T-Mobile", "role": "CMO Europe", "sector": "Enterprise/Telecom", "start": 2000, "end": 2004, "note": None},
            {"company": "Google", "role": "SVP & Chief Business Officer", "sector": "Enterprise", "start": 2004, "end": 2014, "note": "Ran Google's revenue operations"},
            {"company": "SoftBank", "role": "President & COO", "sector": "VC", "start": 2014, "end": 2016, "note": "Heir apparent to Masa Son"},
            {"company": "Palo Alto Networks", "role": "CEO & Chairman", "sector": "Cybersecurity/Defense Tech", "start": 2018, "end": None, "note": "Largest pure-play cybersecurity company"}
        ],
        "sectorSwitches": [
            {"from": "Enterprise", "to": "VC & Finance", "year": 2014},
            {"from": "VC & Finance", "to": "Defense", "year": 2018}
        ]
    },
    {
        "name": "Sridhar Ramaswamy",
        "id": "sridhar-ramaswamy",
        "primarySector": "Enterprise",
        "source": "https://en.wikipedia.org/wiki/Sridhar_Ramaswamy",
        "roles": [
            {"company": "Google", "role": "SVP Ads & Commerce", "sector": "Enterprise/Advertising", "start": 2003, "end": 2018, "note": "Built $200B+ ads business"},
            {"company": "Neeva", "role": "Co-founder & CEO", "sector": "AI/Search", "start": 2019, "end": 2023, "note": "Ad-free AI search, acquired by Snowflake"},
            {"company": "Snowflake", "role": "CEO", "sector": "Enterprise/Cloud", "start": 2024, "end": None, "note": "Succeeded Frank Slootman"}
        ],
        "sectorSwitches": [
            {"from": "Enterprise", "to": "AI", "year": 2019},
            {"from": "AI", "to": "Enterprise", "year": 2024}
        ]
    },
    {
        "name": "Sarah Friar",
        "id": "sarah-friar",
        "primarySector": "Social & Media",
        "source": "https://en.wikipedia.org/wiki/Sarah_Friar",
        "roles": [
            {"company": "Goldman Sachs", "role": "Analyst", "sector": "Finance", "start": 1996, "end": 2000, "note": None},
            {"company": "Salesforce", "role": "VP Finance", "sector": "Enterprise", "start": 2006, "end": 2012, "note": None},
            {"company": "Square", "role": "CFO", "sector": "Fintech", "start": 2012, "end": 2018, "note": "Through IPO and hypergrowth"},
            {"company": "Nextdoor", "role": "CEO", "sector": "Social Media", "start": 2018, "end": None, "note": "Neighborhood social network, took public via SPAC"}
        ],
        "sectorSwitches": [
            {"from": "VC & Finance", "to": "Enterprise", "year": 2006},
            {"from": "Enterprise", "to": "Fintech", "year": 2012},
            {"from": "Fintech", "to": "Social & Media", "year": 2018}
        ]
    },
    {
        "name": "Logan Green",
        "id": "logan-green",
        "primarySector": "Consumer",
        "source": "https://en.wikipedia.org/wiki/Logan_Green",
        "roles": [
            {"company": "Zimride", "role": "Co-founder & CEO", "sector": "Consumer Tech/Ridesharing", "start": 2007, "end": 2012, "note": "Long-distance ridesharing"},
            {"company": "Lyft", "role": "Co-founder & CEO", "sector": "Consumer Tech/Ridesharing", "start": 2012, "end": 2023, "note": "IPO 2019, stepped down as CEO 2023"},
            {"company": "Climate Tech Investing", "role": "Investor", "sector": "Deep Tech/Climate", "start": 2023, "end": None, "note": "Focus on transportation decarbonization"}
        ],
        "sectorSwitches": [
            {"from": "Consumer", "to": "Deep Tech", "year": 2023}
        ]
    },
    {
        "name": "Adam D'Angelo",
        "id": "adam-dangelo",
        "primarySector": "Consumer",
        "source": "https://en.wikipedia.org/wiki/Adam_D%27Angelo",
        "roles": [
            {"company": "Facebook", "role": "CTO & VP Engineering", "sector": "Social Media", "start": 2006, "end": 2008, "note": "One of first engineers"},
            {"company": "Quora", "role": "Co-founder & CEO", "sector": "Consumer Tech", "start": 2009, "end": None, "note": "Q&A platform, also launched Poe AI chatbot"},
            {"company": "OpenAI", "role": "Board Member", "sector": "AI", "start": 2023, "end": None, "note": "Joined board, key figure in Altman firing/reinstatement drama"}
        ],
        "sectorSwitches": [
            {"from": "Social & Media", "to": "Consumer", "year": 2009}
        ]
    },
    {
        "name": "Jaan Tallinn",
        "id": "jaan-tallinn",
        "primarySector": "Deep Tech",
        "source": "https://en.wikipedia.org/wiki/Jaan_Tallinn",
        "roles": [
            {"company": "Kazaa", "role": "Co-founder & Lead Developer", "sector": "Consumer Tech", "start": 2000, "end": 2002, "note": "P2P file sharing"},
            {"company": "Skype", "role": "Co-founder & Lead Engineer", "sector": "Consumer Tech/Communications", "start": 2003, "end": 2005, "note": "Sold to eBay for $2.6B"},
            {"company": "Future of Life Institute", "role": "Co-founder", "sector": "AI Safety/Research", "start": 2014, "end": None, "note": "AI existential risk"},
            {"company": "Centre for the Study of Existential Risk", "role": "Co-founder", "sector": "AI Safety/Research", "start": 2012, "end": None, "note": "Cambridge University"},
            {"company": "Metaplanet", "role": "Founder", "sector": "VC", "start": 2014, "end": None, "note": "Investing in AI safety and deep tech"}
        ],
        "sectorSwitches": [
            {"from": "Consumer", "to": "AI", "year": 2012}
        ]
    },
]


def upsert_founder(f):
    """Insert a single founder + roles + switches into Supabase."""
    fid = f['id']

    # Upsert founder row
    founder_row = json.dumps({
        'id': fid,
        'name': f['name'],
        'primary_sector': f.get('primarySector', 'Other'),
        'source_url': f.get('source', ''),
        'verified': None,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/founders",
        data=founder_row,
        headers={**HEADERS, 'Prefer': 'resolution=merge-duplicates'},
        method='POST'
    )
    urllib.request.urlopen(req, timeout=10)

    # Insert roles
    for i, role in enumerate(f.get('roles', [])):
        role_row = json.dumps({
            'founder_id': fid,
            'company': role.get('company', ''),
            'role': role.get('role', ''),
            'sector': role.get('sector', 'Other'),
            'start_year': role.get('start'),
            'end_year': role.get('end'),
            'note': role.get('note'),
            'sort_order': i,
        }).encode()
        req = urllib.request.Request(
            f"{BASE}/roles",
            data=role_row,
            headers=HEADERS,
            method='POST'
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f"  Warning role insert for {fid}: {e}", file=sys.stderr)

    # Insert sector switches
    for switch in f.get('sectorSwitches', []):
        switch_row = json.dumps({
            'founder_id': fid,
            'from_sector': switch.get('from', ''),
            'to_sector': switch.get('to', ''),
            'year': switch.get('year'),
        }).encode()
        req = urllib.request.Request(
            f"{BASE}/sector_switches",
            data=switch_row,
            headers=HEADERS,
            method='POST'
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            print(f"  Warning switch insert for {fid}: {e}", file=sys.stderr)


def main():
    # First check existing IDs to avoid duplicates
    req = urllib.request.Request(
        f"{BASE}/founders?select=id",
        headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
    )
    resp = urllib.request.urlopen(req, timeout=15)
    existing = {r['id'] for r in json.loads(resp.read().decode())}
    print(f"Existing founders: {len(existing)}")

    added = 0
    skipped = 0
    for f in FOUNDERS:
        if f['id'] in existing:
            print(f"  SKIP (exists): {f['name']}")
            skipped += 1
            continue
        try:
            upsert_founder(f)
            print(f"  + {f['name']} ({len(f.get('roles', []))} roles, {len(f.get('sectorSwitches', []))} switches)")
            added += 1
        except Exception as e:
            print(f"  ERROR {f['name']}: {e}", file=sys.stderr)

    print(f"\nDone! Added {added}, skipped {skipped} (already existed). Total should be {len(existing) + added}.")


if __name__ == '__main__':
    main()
