/**
 * TGQQ global boot — imported from the very top of `src/index.ts`, so the QQ
 * skin starts at the first page load (login/auth pages included), before the
 * signed-in `initTgqq` shell mounts.
 *
 * Responsibilities:
 *  1. `tq-app` class on <html> — gates the global QQ surface CSS.
 *  2. Kill Telegram's page-wide wallpaper layer (chatBackground.tsx singleton
 *     attaches a bare body-level div with canvases). Marked with a stable
 *     class so `TqGlobal.scss` can hide it.
 *  3. Branding: WebQQ title, QQ favicons, manifest rewrite.
 */
import './design/TqGlobal.scss';

const APP_TITLE = 'WebQQ';
const APP_DESCRIPTION = 'QQ 风格的消息应用 · 基于 Telegram Web';

// Single SVG icon — vector favicon + manifest icon. Vite inlines it as a
// data URI (<4 KB), so no separate raster assets are shipped.
const QQ_ICON_SVG = new URL('./assets/qq-icon.svg', import.meta.url).href;

document.documentElement.classList.add('tq-app');

// ---- Branding --------------------------------------------------------------

function applyBranding() {
  document.title = APP_TITLE;

  for(const name of ['application-name', 'mobile-web-app-title', 'apple-mobile-web-app-title']) {
    document.querySelector(`meta[name="${name}"]`)?.setAttribute('content', APP_TITLE);
  }
  for(const prop of ['og:title', 'twitter:title']) {
    document.querySelector(`meta[property="${prop}"]`)?.setAttribute('content', APP_TITLE);
  }
  for(const prop of ['og:description', 'twitter:description']) {
    document.querySelector(`meta[property="${prop}"]`)?.setAttribute('content', APP_DESCRIPTION);
  }
  document.querySelector('meta[name="description"]')?.setAttribute('content', APP_DESCRIPTION);
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', '#1296db');
  document.querySelector('meta[property="og:image"]')?.setAttribute('content', QQ_ICON_SVG);
  document.querySelector('meta[property="twitter:image"]')?.setAttribute('content', QQ_ICON_SVG);
  document.querySelector('meta[name="msapplication-TileImage"]')?.setAttribute('content', QQ_ICON_SVG);

  for(const link of Array.from(document.querySelectorAll<HTMLLinkElement>('link[rel~="icon"], link[rel="alternate icon"], link[rel="apple-touch-icon"]'))) {
    link.href = QQ_ICON_SVG;
    link.type = 'image/svg+xml';
    // Vector icon is resolution-independent; drop the fixed PNG sizes.
    if(link.getAttribute('sizes')) link.setAttribute('sizes', 'any');
  }
}

async function applyManifest() {
  // `setManifest()` in src/index.ts points #manifest at site.webmanifest on
  // DOMContentLoaded; run after it so we rewrite the real target.
  const manifestLink = document.getElementById('manifest') as HTMLLinkElement | null;
  if(!manifestLink) return;

  let manifest: Record<string, unknown> | null = null;
  try {
    const res = await fetch(manifestLink.href);
    if(res.ok) manifest = await res.json();
  } catch(err) {
    // Offline / no upstream manifest (local builds copy nothing from public/) —
    // fall back to a self-built manifest below.
  }
  if(!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) {
    manifest = {
      name: APP_TITLE,
      short_name: APP_TITLE,
      description: APP_DESCRIPTION,
      start_url: './',
      scope: './',
      display: 'standalone'
    };
  }

  manifest.name = APP_TITLE;
  manifest.short_name = APP_TITLE;
  manifest.description = APP_DESCRIPTION;
  manifest.theme_color = '#1296db';
  manifest.background_color = '#f3f2f7';
  manifest.icons = [
    {src: QQ_ICON_SVG, sizes: 'any', type: 'image/svg+xml'}
  ];
  manifestLink.href = URL.createObjectURL(new Blob([JSON.stringify(manifest)], {type: 'application/manifest+json'}));
}

// ---- Telegram wallpaper layer hiding ---------------------------------------

const BG_LAYER_CLASS = 'tq-bg-layer';

/**
 * The wallpaper singleton creates a bare `<div>` (no id/class), inserts it as
 * body's first child, then Solid-renders gradient/pattern canvases inside.
 * Anything with an id or class (auth pages, #page-chats, overlays) can't be it.
 */
function isTelegramBackgroundLayer(el: Element): boolean {
  if(!(el instanceof HTMLElement) || el.parentElement !== document.body) return false;
  if(el.id || el.className.trim()) return false;
  return !!el.querySelector('canvas');
}

function markBackgroundLayers() {
  for(const child of Array.from(document.body.children)) {
    if(isTelegramBackgroundLayer(child) && !child.classList.contains(BG_LAYER_CLASS)) {
      child.classList.add(BG_LAYER_CLASS);
    }
  }
}

function startBackgroundHiding() {
  markBackgroundLayers();
  // Canvas render happens a tick after the layer div is inserted; rescan.
  new MutationObserver(() => {
    markBackgroundLayers();
    window.setTimeout(markBackgroundLayers, 250);
  }).observe(document.body, {childList: true});
  window.setTimeout(markBackgroundLayers, 500);
  window.setTimeout(markBackgroundLayers, 2000);
}

applyBranding();

if(document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    startBackgroundHiding();
    window.setTimeout(applyManifest, 0);
  }, {once: true});
} else {
  startBackgroundHiding();
  applyManifest();
}
