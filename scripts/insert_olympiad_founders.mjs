#!/usr/bin/env node

import fs from 'node:fs';

const envText = fs.readFileSync(new URL('../.env', import.meta.url), 'utf8');
const env = Object.fromEntries(
  envText
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#') && line.includes('='))
    .map((line) => {
      const idx = line.indexOf('=');
      return [line.slice(0, idx), line.slice(idx + 1)];
    })
);

const SUPABASE_URL = 'https://tnmbxxcdabecqknzxuus.supabase.co';
const SUPABASE_SERVICE_KEY = env.SUPABASE_SERVICE_KEY;

if (!SUPABASE_SERVICE_KEY) {
  console.error('Missing SUPABASE_SERVICE_KEY in .env');
  process.exit(1);
}

const FOUNDERS = [
  {
    id: 'jesse-zhang',
    name: 'Jesse Zhang',
    primarySector: 'AI',
    source_url: 'https://techcrunch.com/2024/06/18/decagon-claims-its-customers-service-bots-are-smarter-than-average/',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Google',
        role: 'Intern',
        sector: 'Enterprise Software',
        start_year: 2016,
        end_year: 2016,
        note: 'Public LinkedIn profile lists a 2016 internship at Google',
      },
      {
        company: 'Hudson River Trading',
        role: 'Intern',
        sector: 'Quantitative Trading',
        start_year: 2016,
        end_year: 2016,
        note: 'Public LinkedIn profile lists a 2016 internship at Hudson River Trading',
      },
      {
        company: 'Citadel',
        role: 'Intern',
        sector: 'Quantitative Trading',
        start_year: 2017,
        end_year: 2017,
        note: 'Public LinkedIn profile lists a 2017 internship at Citadel',
      },
      {
        company: 'Lowkey',
        role: 'Founder & CEO',
        sector: 'Gaming',
        start_year: 2018,
        end_year: 2022,
        note: 'Founded the gaming-social startup acquired by Niantic in December 2021',
      },
      {
        company: 'Decagon',
        role: 'Co-founder & CEO',
        sector: 'AI Agents',
        start_year: 2023,
        end_year: null,
        note: 'Co-founded the enterprise AI agent company',
      },
    ],
    sector_switches: [
      { from_sector: 'Fintech', to_sector: 'Social & Media', year: 2018 },
      { from_sector: 'Social & Media', to_sector: 'AI', year: 2023 },
    ],
  },
  {
    id: 'jeff-yan',
    name: 'Jeff Yan',
    primarySector: 'Crypto',
    source_url: 'https://colossus.com/article/beyond-the-sky-jeffrey-yan-hyperliquid/',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Chameleon Trading',
        role: 'Co-founder',
        sector: 'Quantitative Trading',
        start_year: 2020,
        end_year: 2023,
        note: 'Built a quantitative trading firm before Hyperliquid',
      },
      {
        company: 'Hyperliquid',
        role: 'Co-founder',
        sector: 'Crypto Exchange',
        start_year: 2023,
        end_year: null,
        note: 'Co-founded the perpetuals exchange',
      },
    ],
    sector_switches: [
      { from_sector: 'Fintech', to_sector: 'Crypto', year: 2023 },
    ],
  },
  {
    id: 'johnny-ho',
    name: 'Johnny Ho',
    primarySector: 'AI',
    source_url: 'https://www.forbes.com/profile/johnny-ho/',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Quora',
        role: 'Engineer',
        sector: 'Consumer Internet',
        start_year: 2017,
        end_year: 2020,
        note: 'Public bios list Quora before Tower Research; years are inferred between Harvard graduation and Perplexity founding',
      },
      {
        company: 'Tower Research Capital',
        role: 'Quantitative Trader',
        sector: 'Quantitative Trading',
        start_year: 2020,
        end_year: 2022,
        note: 'Public bios list Tower Research Capital immediately before Perplexity; years are inferred before the August 2022 founding',
      },
      {
        company: 'Perplexity',
        role: 'Co-founder & CSO',
        sector: 'AI/Search',
        start_year: 2022,
        end_year: null,
        note: 'Co-founded the AI answer engine',
      },
    ],
    sector_switches: [
      { from_sector: 'Fintech', to_sector: 'AI', year: 2022 },
    ],
  },
  {
    id: 'demi-guo',
    name: 'Demi Guo',
    primarySector: 'AI',
    source_url: 'https://theorg.com/org/pika-1/org-chart/demi-guo',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Facebook AI Research',
        role: 'Research Engineer',
        sector: 'Research / AI',
        start_year: 2020,
        end_year: 2021,
        note: 'Public bios describe a full-time research engineering role at Facebook AI Research before Stanford',
      },
      {
        company: 'Stanford University',
        role: 'Doctoral Student',
        sector: 'Academia / AI',
        start_year: 2021,
        end_year: 2023,
        note: 'Stanford and public bios show a PhD track in computer science focused on NLP and graphics before founding Pika',
      },
      {
        company: 'Pika',
        role: 'Co-founder & CEO',
        sector: 'AI Video',
        start_year: 2023,
        end_year: null,
        note: 'Co-founded the generative video startup',
      },
    ],
    sector_switches: [
      { from_sector: 'Research', to_sector: 'AI', year: 2023 },
    ],
  },
  {
    id: 'vladimir-novakovski',
    name: 'Vladimir Novakovski',
    primarySector: 'Crypto',
    source_url: 'https://lighterhub.xyz/',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Quora',
        role: 'Head of Machine Learning',
        sector: 'AI / Machine Learning',
        start_year: 2012,
        end_year: 2014,
        note: 'Lighter Hub publicly lists Quora Head of Machine Learning from 2012 to 2014',
      },
      {
        company: 'Addepar',
        role: 'VP Engineering',
        sector: 'Finance Software',
        start_year: 2014,
        end_year: 2015,
        note: 'Addepar identified him as VP of Engineering in August 2014; public bios show this role through 2015',
      },
      {
        company: 'Lunchclub',
        role: 'Co-founder & CEO',
        sector: 'Professional Social Network',
        start_year: 2017,
        end_year: 2022,
        note: 'Public profiles describe him as a Lunchclub co-founder before Lighter',
      },
      {
        company: 'Lighter',
        role: 'Co-founder & CEO',
        sector: 'Crypto Exchange',
        start_year: 2022,
        end_year: null,
        note: 'Co-founded the onchain perpetuals exchange',
      },
    ],
    sector_switches: [
      { from_sector: 'AI', to_sector: 'Fintech', year: 2014 },
      { from_sector: 'Fintech', to_sector: 'Social & Media', year: 2017 },
      { from_sector: 'Social & Media', to_sector: 'Crypto', year: 2022 },
    ],
  },
  {
    id: 'eugene-chen',
    name: 'Eugene Chen',
    primarySector: 'Crypto',
    source_url: 'https://quip.com/blog/shared-with-me',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Addepar',
        role: 'Software Engineer',
        sector: 'Finance Software',
        start_year: 2014,
        end_year: 2014,
        note: 'Addepar named him as a software engineer in its August 2014 HackerRank contest announcement',
      },
      {
        company: 'Quip',
        role: 'Software Engineer',
        sector: 'Enterprise Collaboration',
        start_year: 2018,
        end_year: 2022,
        note: 'A Quip engineering blog post from August 2018 is authored by Eugene Chen; public bios list Quip before Ellipsis Labs',
      },
      {
        company: 'Ellipsis Labs',
        role: 'Co-founder & CEO',
        sector: 'Crypto Infrastructure',
        start_year: 2022,
        end_year: null,
        note: 'Co-founded Ellipsis Labs, the team behind Phoenix and Atlas',
      },
    ],
    sector_switches: [
      { from_sector: 'Enterprise', to_sector: 'Crypto', year: 2022 },
    ],
  },
  {
    id: 'walden-yan',
    name: 'Walden Yan',
    primarySector: 'AI',
    source_url: 'https://cognition.ai/',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Cognition',
        role: 'Co-founder',
        sector: 'AI',
        start_year: 2023,
        end_year: null,
        note: 'Founding team behind Devin',
      },
    ],
    sector_switches: [],
  },
  {
    id: 'steven-hao',
    name: 'Steven Hao',
    primarySector: 'AI',
    source_url: 'https://cognition.ai/',
    verified: '2026-04-14',
    roles: [
      {
        company: 'Cognition',
        role: 'Co-founder',
        sector: 'AI',
        start_year: 2023,
        end_year: null,
        note: 'Founding team behind Devin',
      },
    ],
    sector_switches: [],
  },
];

async function request(path, { method = 'GET', body, prefer } = {}) {
  const headers = {
    apikey: SUPABASE_SERVICE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
  };
  if (body) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') headers.Prefer = prefer || 'return=minimal';

  const response = await fetch(`${SUPABASE_URL}/rest/v1${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${method} ${path} failed: ${response.status} ${text}`);
  }

  if (response.status === 204) return null;
  const text = await response.text();
  if (!text) return null;
  return JSON.parse(text);
}

async function main() {
  const ids = FOUNDERS.map((founder) => founder.id).join(',');
  const existingRows = await request(`/founders?select=id&id=in.(${ids})`);
  const existingIds = new Set((existingRows || []).map((row) => row.id));

  for (const founder of FOUNDERS) {
    const founderRow = {
      id: founder.id,
      name: founder.name,
      primary_sector: founder.primarySector,
      source_url: founder.source_url,
      verified: founder.verified,
    };

    await request('/founders?on_conflict=id', {
      method: 'POST',
      body: founderRow,
      prefer: 'resolution=merge-duplicates,return=minimal',
    });
    await request(`/roles?founder_id=eq.${founder.id}`, { method: 'DELETE' });
    await request(`/sector_switches?founder_id=eq.${founder.id}`, { method: 'DELETE' });

    for (let i = 0; i < founder.roles.length; i += 1) {
      const role = founder.roles[i];
      await request('/roles', {
        method: 'POST',
        body: {
          founder_id: founder.id,
          company: role.company,
          role: role.role,
          sector: role.sector,
          start_year: role.start_year,
          end_year: role.end_year,
          note: role.note,
          sort_order: i,
        },
      });
    }

    for (const sectorSwitch of founder.sector_switches) {
      await request('/sector_switches', {
        method: 'POST',
        body: {
          founder_id: founder.id,
          from_sector: sectorSwitch.from_sector,
          to_sector: sectorSwitch.to_sector,
          year: sectorSwitch.year,
        },
      });
    }

    console.log(`${existingIds.has(founder.id) ? 'refreshed' : 'inserted'} ${founder.id}`);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
