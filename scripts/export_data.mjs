// Export Supabase tables to static JSON files in data/.
// Usage: node scripts/export_data.mjs
// Supabase remains the offline source of truth; the site reads these JSON files at runtime.

import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SUPABASE_URL = 'https://tnmbxxcdabecqknzxuus.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubWJ4eGNkYWJlY3Frbnp4dXVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM3OTE5MTcsImV4cCI6MjA4OTM2NzkxN30.xL4gRw-_JXifwFu4L7g3rZigSAqK9z8cs7YuMlQD28w';
const PAGE_SIZE = 1000;

const HEADERS = {
  apikey: SUPABASE_ANON_KEY,
  Authorization: `Bearer ${SUPABASE_ANON_KEY}`
};

const DATA_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'data');

async function fetchAllRows(table, extraParams = {}) {
  const rows = [];
  for (let offset = 0; ; offset += PAGE_SIZE) {
    const params = new URLSearchParams({
      select: '*',
      offset: String(offset),
      limit: String(PAGE_SIZE),
      ...extraParams
    });
    const response = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${params.toString()}`, {
      headers: HEADERS
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Supabase REST ${table} ${response.status}: ${text || response.statusText}`);
    }
    const page = await response.json();
    rows.push(...page);
    if (page.length < PAGE_SIZE) break;
  }
  return rows;
}

async function exportTable(table, extraParams = {}) {
  const rows = await fetchAllRows(table, extraParams);
  const outPath = path.join(DATA_DIR, `${table}.json`);
  await writeFile(outPath, JSON.stringify(rows, null, 2) + '\n');
  console.log(`${table}: ${rows.length} rows -> ${path.relative(process.cwd(), outPath)}`);
  return rows.length;
}

await mkdir(DATA_DIR, { recursive: true });
await exportTable('founders');
await exportTable('roles', { order: 'sort_order.asc,id.asc' });
await exportTable('sector_switches');
console.log('Done.');
