// Find layout problems in a Slidev deck. Usage:
//   node check_overflow.mjs <deck>.md [port] [--ignore=.sel1,.sel2]
// --ignore: CSS selectors of decorative elements that may cross the edge
// (e.g. a custom cover layout), skipped in the overflow test.
// Starts its OWN private dev server (localhost only, random port; never the user's
// running server: Slidev syncs navigation, so screenshots there move the
// user's slides), visits every slide with all clicks shown and prints one line
// per problem: "slide N: <kind> <detail>".
//   overflow ...      content runs past the slide edge (must fix)
//   NOT RENDERED      compile error or missing file (fix first)
//   broken image      image not found
//   SMALL TEXT        body text below 15px (base ~21px)
//   ROOM              text below 18px while the slide is less than 80% filled
//   UNDERFILLED       content ends above 65% of the height
// Slidev and playwright-chromium are taken from $SLIDEV_RUNTIME, the deck's
// node_modules, or ~/.local/share/slidev-runtime.
import { spawn } from 'node:child_process'
import { createRequire } from 'node:module'
import { existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, resolve } from 'node:path'

const deck = resolve(process.argv[2])
const cands = [process.env.SLIDEV_RUNTIME, dirname(deck), resolve(dirname(deck), '..'), `${homedir()}/.local/share/slidev-runtime`]
const RUNTIME = cands.find(d => d && existsSync(`${d}/node_modules/.bin/slidev`))
if (!RUNTIME) { console.error('Slidev not found: set SLIDEV_RUNTIME to a folder with node_modules/.bin/slidev and playwright-chromium'); process.exit(2) }
const { chromium } = createRequire(`${RUNTIME}/package.json`)('playwright-chromium')
const SLIDEV = `${RUNTIME}/node_modules/.bin/slidev`

const IGNORE = (process.argv.find(a => a.startsWith('--ignore=')) || '--ignore=').slice(9).split(',').filter(Boolean)
const portArg = process.argv.slice(3).find(a => /^\d+$/.test(a))
const port = portArg || String(3100 + Math.floor(Math.random() * 800))
const server = spawn(SLIDEV, [deck, '--port', port], { stdio: 'pipe', cwd: dirname(deck) })

async function waitForServer() {
  for (let i = 0; i < 120; i++) {
    try {
      const r = await fetch(`http://localhost:${port}/`)
      if (r.ok) return
    } catch {}
    await new Promise(r => setTimeout(r, 500))
  }
  throw new Error('dev server did not start')
}

try {
  await waitForServer()
  const browser = await chromium.launch()
  const page = await browser.newPage({ viewport: { width: 980, height: 551 } })
  await page.goto(`http://localhost:${port}/1`, { waitUntil: 'load', timeout: 90000 })
  await page.waitForSelector('.slidev-layout', { timeout: 90000 })
  const total = await page.evaluate(() => window.__slidev__?.nav?.total ?? 0)
  const problems = [`slides: ${total}`]
  for (let n = 1; n <= total; n++) {
    await page.goto(`http://localhost:${port}/${n}?clicks=99`, { waitUntil: 'load' })
    await page.waitForTimeout(400)
    await page.waitForFunction(() => [...document.querySelectorAll('.slidev-page .slidev-layout')].some(l => l.getBoundingClientRect().height > 0), null, { timeout: 15000 }).catch(() => {})
    await page.waitForTimeout(500)
    const found = await page.evaluate((IGNORE) => {
      const out = []
      const layout = [...document.querySelectorAll('.slidev-page')]
        .map(p => p.querySelector('.slidev-layout'))
        .find(l => l && l.getBoundingClientRect().height > 0)
      if (!layout) return ['NOT RENDERED (compile error or missing image?)']
      const box = layout.getBoundingClientRect()
      const tol = 2
      for (const el of layout.querySelectorAll('*')) {
        if (el.closest('.source') || el.closest('.katex') || IGNORE.some(sel => el.closest(sel))) continue
        const r = el.getBoundingClientRect()
        if (r.width === 0 || r.height === 0) continue
        const isLeaf = el.children.length === 0 || ['IMG', 'svg', 'TABLE'].includes(el.tagName)
        if (!isLeaf) continue
        if (r.bottom > box.bottom + tol || r.right > box.right + tol || r.left < box.left - tol || r.top < box.top - tol) {
          const txt = (el.innerText || el.getAttribute('src') || el.tagName).slice(0, 50).replace(/\s+/g, ' ')
          out.push(`overflow ${el.tagName.toLowerCase()} "${txt}" bottom+${Math.round(r.bottom - box.bottom)} right+${Math.round(r.right - box.right)}`)
          break
        }
      }
      // fill / text-size heuristics (canvas px; base text is ~21px)
      if (!/cover|center|section|intro|end|fact|quote|statement/.test(layout.className)) {
        let bottom = 0, minFont = 99, textChars = 0
        for (const el of layout.querySelectorAll('*')) {
          if (el.closest('.source') || el.closest('.katex') || el.tagName === 'H1') continue
          const r = el.getBoundingClientRect()
          if (r.width === 0 || r.height === 0) continue
          const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('')
          if (el.children.length === 0 || el.tagName === 'IMG' || own.length > 0) bottom = Math.max(bottom, r.bottom - box.top)
          if (own.length > 3 && !el.closest('pre')) {
            minFont = Math.min(minFont, parseFloat(getComputedStyle(el).fontSize)); textChars += own.length
          }
        }
        const fill = Math.round(100 * bottom / box.height)
        if (textChars > 40 && minFont < 15) out.push(`SMALL TEXT min ${minFont.toFixed(0)}px, content ends at ${fill}% of height`)
        else if (textChars > 40 && minFont < 18 && fill < 80) out.push(`ROOM text min ${minFont.toFixed(0)}px but content ends at ${fill}% — text/images could be bigger`)
        else if (fill < 65) out.push(`UNDERFILLED content ends at ${fill}% of height`)
      }
      for (const img of layout.querySelectorAll('img')) {
        if (img.complete && img.naturalWidth === 0) out.push(`broken image ${img.getAttribute('src')}`)
      }
      return out
    }, IGNORE)
    for (const f of found) problems.push(`slide ${n}: ${f}`)
  }
  console.log(problems.join('\n'))
  await browser.close()
} finally {
  server.kill()
}
