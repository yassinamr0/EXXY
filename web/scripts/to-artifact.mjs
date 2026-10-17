// Turns the single-file build into a page fragment for the private preview
// host, which supplies its own <html>/<head>/<body> wrapper.
import { readFileSync, writeFileSync } from 'node:fs'

const html = readFileSync(new URL('../dist-single/index.html', import.meta.url), 'utf8')
const grab = (re) => [...html.matchAll(re)].map((m) => m[0]).join('\n')
const out = [
  grab(/<title>[\s\S]*?<\/title>/g),
  '<meta name="robots" content="noindex, nofollow">',
  grab(/<style[\s\S]*?<\/style>/g),
  '<div id="root"></div>',
  grab(/<script[\s\S]*?<\/script>/g),
].join('\n')
writeFileSync(new URL('../dist-single/artifact.html', import.meta.url), out)
console.log(`artifact.html: ${(out.length / 1024).toFixed(0)} KB`)
