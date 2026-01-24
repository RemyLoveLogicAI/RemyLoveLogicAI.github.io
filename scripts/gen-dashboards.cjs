#!/usr/bin/env node
const { readdirSync, statSync, writeFileSync } = require('node:fs')
const { resolve, relative, sep } = require('node:path')

const ROOT = resolve(__dirname, '..')
const PUBLIC = resolve(ROOT, 'public')
const ASSETS = resolve(PUBLIC, 'static', 'assets')

function walk(dir) {
  let out = []
  for (const name of readdirSync(dir)) {
    const p = resolve(dir, name)
    const s = statSync(p)
    if (s.isDirectory()) out = out.concat(walk(p))
    else out.push(p)
  }
  return out
}

function relUrl(abs) {
  const r = '/' + relative(PUBLIC, abs).split(sep).join('/')
  return r
}

function main() {
  const paths = walk(ASSETS)
  const entries = []
  for (const p of paths) {
    if (!p.toLowerCase().endsWith('.html')) continue
    const url = relUrl(p)
    const parts = url.split('/')
    const name = parts[parts.length - 1]
    const folder = parts.slice(0, parts.length - 1).join('/')
    entries.push({ name, folder, url })
  }
  entries.sort((a,b) => a.url.localeCompare(b.url))
  const out = { generatedAt: new Date().toISOString(), entries }
  const target = resolve(ASSETS, 'dashboards.json')
  writeFileSync(target, JSON.stringify(out, null, 2))
  console.log(`[gen-dashboards] wrote ${target} with ${entries.length} entries`)
}

main()