#!/usr/bin/env node
/**
 * sync-game.mjs
 *
 * Copies the reachable subset of the designer's HTML game source (SVN working copy)
 * into public/game/, preserving relative folder structure, and injects a small
 * postMessage hook into every stage HTML file so React can detect stage completion.
 *
 * public/game/ is fully regenerated on every run (deleted then recreated) — never
 * hand-edit anything under it, your changes will be wiped on the next sync.
 *
 * Usage:
 *   node scripts/sync-game.mjs [--source <path>] [--theme <B-1..B-6>] [--dry-run]
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, '..');
const DEFAULT_SOURCE = 'E:\\01_Work\\06_KinderCoding\\03-Work\\Coding';
const OUTPUT_ROOT = path.join(PROJECT_ROOT, 'public', 'game');
const REPORT_PATH = path.join(__dirname, 'sync-report.json');

const EXCLUDED_DIR_NAMES = new Set(['_old', '공유', '비주얼컨셉안', '이전작업']);
// Some JS data arrays store asset paths as fragments relative to one of these shared
// root folders (e.g. icon:'B_1/img_x.svg' meaning img_svg/B_1/img_x.svg) instead of
// relative to the referencing file. Tried as a fallback when direct resolution fails.
const SHARED_ASSET_ROOTS = ['img_svg', 'img_png', 'audio', 'fonts'];

const TEXT_EXTENSIONS = new Set(['.html', '.htm', '.css', '.js', '.mjs']);
const PATH_LIKE_EXTENSIONS =
  'html|htm|css|js|mjs|png|jpe?g|svg|gif|webp|mp3|wav|ogg|json|woff2?|ttf|otf';

function parseArgs(argv) {
  const args = { source: DEFAULT_SOURCE, theme: null, dryRun: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--source') args.source = argv[++i];
    else if (a === '--theme') args.theme = argv[++i];
    else if (a === '--dry-run') args.dryRun = true;
  }
  return args;
}

function hasExcludedSegment(absPath, sourceRoot) {
  const rel = path.relative(sourceRoot, absPath);
  const segments = rel.split(path.sep);
  return segments.some((seg) => EXCLUDED_DIR_NAMES.has(seg));
}

function isExternalRef(ref) {
  return /^(https?:)?\/\//i.test(ref) || /^(data|mailto|tel|javascript):/i.test(ref);
}

function stripQueryAndHash(ref) {
  return ref.split('#')[0].split('?')[0];
}

/** Extract candidate reference strings from file content, by extension. */
function extractReferences(ext, text) {
  const refs = new Set();

  if (ext === '.html' || ext === '.htm') {
    for (const m of text.matchAll(/(?:href|src)\s*=\s*["']([^"'#?][^"']*)["']/gi)) {
      refs.add(m[1]);
    }
  }
  if (ext === '.css' || ext === '.html' || ext === '.htm') {
    // Lowercase-only, no /i flag: avoids matching identifiers like loadingUrl(...)
    // or the JS `new URL(href, base)` constructor (two args, unrelated to CSS url()).
    for (const m of text.matchAll(/(?<![a-zA-Z0-9_])url\(\s*["']?([^"')]+)["']?\s*\)/g)) {
      refs.add(m[1]);
    }
  }
  if (ext === '.js' || ext === '.mjs' || ext === '.html' || ext === '.htm') {
    for (const m of text.matchAll(/(?:new\s+Audio\(|\.src\s*=\s*)["']([^"']+)["']/gi)) {
      refs.add(m[1]);
    }
    // Generic quoted relative-path literal ending in a known extension
    // (covers array elements like NODES[].href = '../B-1_x/B-1_01.html')
    const genericRe = new RegExp(
      `["']((?:\\.\\./)*[^"'\\s]+?\\.(?:${PATH_LIKE_EXTENSIONS}))["']`,
      'gi'
    );
    for (const m of text.matchAll(genericRe)) {
      refs.add(m[1]);
    }
  }
  if (ext === '.html' || ext === '.htm') {
    const genericRe = new RegExp(
      `["']((?:\\.\\./)*[^"'\\s]+?\\.(?:${PATH_LIKE_EXTENSIONS}))["']`,
      'gi'
    );
    for (const m of text.matchAll(genericRe)) {
      refs.add(m[1]);
    }
  }

  return [...refs].filter((r) => !isExternalRef(r));
}

/** Detect dynamic `'<dirPrefix>/' + var + '.ext'` concatenation and expand to real .html siblings on disk. */
function extractDynamicDirExpansions(text, referencingFileAbs, sourceRoot) {
  const expansions = [];
  const dirConcatRe = /(['"`])((?:\.\.\/)+[^'"`]*\/)\1\s*\+/g;
  for (const m of text.matchAll(dirConcatRe)) {
    const dirPrefix = m[2];
    const resolvedDir = path.resolve(path.dirname(referencingFileAbs), dirPrefix);
    if (hasExcludedSegment(resolvedDir, sourceRoot)) continue;
    if (!fs.existsSync(resolvedDir) || !fs.statSync(resolvedDir).isDirectory()) continue;
    const entries = fs.readdirSync(resolvedDir, { withFileTypes: true });
    const htmlFiles = entries
      .filter((e) => e.isFile() && /\.html?$/i.test(e.name))
      .map((e) => path.join(resolvedDir, e.name));
    if (htmlFiles.length > 0) {
      expansions.push({ dirPrefix, resolvedDir, addedFiles: htmlFiles });
    }
  }
  return expansions;
}

const MAP_PROGRESS_RE = /var\s+ID\s*=\s*'([^']+)'\s*,\s*K\s*=\s*'([^']+)'/;

function buildInjectedSnippet(id, theme, key) {
  return `<script>/* REACT-BRIDGE v1 — injected by scripts/sync-game.mjs, do not hand-edit */
(function(){
  var ID='${id}', THEME='${theme}', K='${key}';
  var done=false;
  function notify(){
    if(done) return;
    if(document.querySelector('#win.on,#win.is-on,[class*="_exit_"]')){
      done = true;
      try{
        window.parent.postMessage({
          source: 'kindercoding-game',
          type: 'stageComplete',
          theme: THEME,
          stage: ID,
          key: K,
          ts: Date.now()
        }, '*');
      }catch(e){}
      mo.disconnect();
    }
  }
  var mo = new MutationObserver(notify);
  mo.observe(document.documentElement, {subtree:true, childList:true, attributes:true, attributeFilter:['class']});
})();
</script>`;
}

/** If this stage HTML has the existing MAP-PROGRESS snippet, inject our postMessage bridge after it. */
function injectStageHook(html, filePathForLog, report) {
  const match = html.match(MAP_PROGRESS_RE);
  if (!match) return html;

  const [, id, key] = match;
  const themeMatch = key.match(/ck\.b(\d+)\.sub\.done/);
  if (!themeMatch) return html;
  const theme = `B-${themeMatch[1]}`;

  if (html.includes('REACT-BRIDGE v1')) return html; // already injected, don't duplicate

  const matchIndex = html.indexOf(match[0]);
  const scriptCloseIndex = html.indexOf('</script>', matchIndex);
  if (scriptCloseIndex === -1) return html;
  const insertAt = scriptCloseIndex + '</script>'.length;

  const snippet = buildInjectedSnippet(id, theme, key);
  report.stageHooksInjected.push({ file: filePathForLog, theme, stage: id, key });
  return html.slice(0, insertAt) + '\n' + snippet + html.slice(insertAt);
}

/** Resolve a candidate ref relative to the referencing file, falling back to shared asset roots. */
function resolveRef(cleanedRef, referencingFile, sourceRoot) {
  const direct = path.resolve(path.dirname(referencingFile), cleanedRef);
  if (fs.existsSync(direct) && fs.statSync(direct).isFile()) return direct;

  for (const root of SHARED_ASSET_ROOTS) {
    const viaRoot = path.resolve(sourceRoot, root, cleanedRef);
    if (fs.existsSync(viaRoot) && fs.statSync(viaRoot).isFile()) return viaRoot;
  }
  return null;
}

function findThemeDir(sourceRoot, theme) {
  const entries = fs.readdirSync(sourceRoot, { withFileTypes: true });
  const dir = entries.find((e) => e.isDirectory() && e.name.startsWith(`${theme}_`));
  return dir ? dir.name : null;
}

function run() {
  const args = parseArgs(process.argv.slice(2));
  const sourceRoot = path.resolve(args.source);

  if (!fs.existsSync(sourceRoot)) {
    console.error(`Source not found: ${sourceRoot}`);
    process.exit(1);
  }

  let themeDirName = null;
  if (args.theme) {
    themeDirName = findThemeDir(sourceRoot, args.theme);
    if (!themeDirName) {
      console.error(`No theme folder matching "${args.theme}_*" found under ${sourceRoot}`);
      process.exit(1);
    }
    console.log(`Theme filter active: only copying B_0_main/, root shared files, and ${themeDirName}/`);
  }

  const seeds = [
    'B_0_main/main.html',
    'B_0_main/A-1_login.html',
    'B_0_main/A-2_profile.html',
    'B_0_main/A-3_parent.html',
    'B_0_main/A-4_allmenu.html',
    'loading.html',
    'DESIGN.css',
    'RESPONSIVE.css',
    'RESPONSIVE.js',
    'EXIT_CONFIRM.js',
  ].map((p) => path.resolve(sourceRoot, p));

  const report = {
    sourceRoot,
    theme: args.theme,
    visited: [],
    unresolved: [],
    dynamicDirExpansions: [],
    stageHooksInjected: [],
  };

  const visited = new Map(); // absPath -> { content: string|null, ext }
  const queue = [...seeds];

  while (queue.length > 0) {
    const current = queue.shift();
    if (visited.has(current)) continue;
    if (!fs.existsSync(current) || !fs.statSync(current).isFile()) {
      report.unresolved.push({ missing: current });
      continue;
    }
    if (hasExcludedSegment(current, sourceRoot)) continue;

    const ext = path.extname(current).toLowerCase();
    const isText = TEXT_EXTENSIONS.has(ext);
    const content = isText ? fs.readFileSync(current, 'utf-8') : null;
    visited.set(current, { content, ext });

    if (isText) {
      const refs = extractReferences(ext, content);
      for (const ref of refs) {
        const cleaned = stripQueryAndHash(ref);
        const resolved = resolveRef(cleaned, current, sourceRoot);
        if (!resolved) {
          report.unresolved.push({ ref, referencedBy: current });
          continue;
        }
        if (visited.has(resolved)) continue;
        if (!hasExcludedSegment(resolved, sourceRoot)) queue.push(resolved);
      }

      if (ext === '.js' || ext === '.html' || ext === '.htm') {
        const expansions = extractDynamicDirExpansions(content, current, sourceRoot);
        for (const exp of expansions) {
          report.dynamicDirExpansions.push({
            referencedBy: current,
            dirPrefix: exp.dirPrefix,
            resolvedDir: exp.resolvedDir,
            addedFiles: exp.addedFiles,
          });
          for (const f of exp.addedFiles) {
            if (!visited.has(f)) queue.push(f);
          }
        }
      }
    }
  }

  report.visited = [...visited.keys()];
  console.log(`BFS complete: ${visited.size} files reachable from seed set.`);
  console.log(`Unresolved references: ${report.unresolved.length}`);
  console.log(`Dynamic directory expansions: ${report.dynamicDirExpansions.length}`);

  if (args.dryRun) {
    fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2));
    console.log(`Dry run only. Report written to ${REPORT_PATH}`);
    return;
  }

  // Regenerate public/game/ from scratch.
  fs.rmSync(OUTPUT_ROOT, { recursive: true, force: true });
  fs.mkdirSync(OUTPUT_ROOT, { recursive: true });

  let copiedCount = 0;
  let copiedBytes = 0;

  for (const [absPath, { content, ext }] of visited) {
    const relPath = path.relative(sourceRoot, absPath);

    if (themeDirName) {
      const topSegment = relPath.split(path.sep)[0];
      const isSharedRootFile = !relPath.includes(path.sep); // no slash => root-level file
      const isAllowed =
        topSegment === 'B_0_main' || topSegment === themeDirName || isSharedRootFile;
      if (!isAllowed) continue;
    }

    const destPath = path.join(OUTPUT_ROOT, relPath);
    fs.mkdirSync(path.dirname(destPath), { recursive: true });

    if (ext === '.html' || ext === '.htm') {
      const finalHtml = injectStageHook(content, relPath, report);
      fs.writeFileSync(destPath, finalHtml, 'utf-8');
      copiedBytes += Buffer.byteLength(finalHtml, 'utf-8');
    } else if (content !== null) {
      fs.writeFileSync(destPath, content, 'utf-8');
      copiedBytes += Buffer.byteLength(content, 'utf-8');
    } else {
      fs.copyFileSync(absPath, destPath);
      copiedBytes += fs.statSync(absPath).size;
    }
    copiedCount++;
  }

  fs.writeFileSync(
    path.join(OUTPUT_ROOT, '.generated-do-not-edit'),
    `Generated by scripts/sync-game.mjs on ${new Date().toISOString()} from ${sourceRoot}.\n` +
      `Do not hand-edit anything under public/game/ — it is wiped and regenerated on every sync run.\n`
  );

  report.copiedCount = copiedCount;
  report.copiedBytes = copiedBytes;
  fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2));

  console.log(`Copied ${copiedCount} files (${(copiedBytes / 1024 / 1024).toFixed(2)} MB) to ${OUTPUT_ROOT}`);
  console.log(`Stage postMessage hooks injected: ${report.stageHooksInjected.length}`);
  console.log(`Report written to ${REPORT_PATH}`);
}

run();
