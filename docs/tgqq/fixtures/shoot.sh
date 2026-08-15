#!/usr/bin/env bash
# Regenerate CSS copies from dist, then take chromium headless screenshots.
# Working chromium flags on this proot env: --use-gl=swiftshader --disable-vulkan
set -e
cd "$(dirname "$0")"
DIST=../../../dist
FX=.
mkdir -p "$FX/css"
cp "$DIST"/index-*.css "$FX/css/tweb.css"
cp "$DIST"/tgqq-*.css "$FX/css/tgqq.css"
mkdir -p "$FX/css/assets/fonts"
cp "$DIST"/assets/fonts/* "$FX/css/assets/fonts/" 2>/dev/null || true
CHROME=/usr/lib/chromium/chromium-headless-shell
OUT="$FX/shots"
mkdir -p "$OUT"
PORT=8910
(nohup python -m http.server $PORT >/tmp/tgqq-http.log 2>&1 &)
sleep 1
for spec in "mobile:390x844:mobile.html" "mobile-chat:390x844:mobile-chat.html" "group-chat:390x844:group-chat.html" "group-chat-tablet:900x700:group-chat.html" "tablet-mid:900x700:tablet.html" "tablet-wide:1180x820:tablet.html" "tablet-xwide:1440x900:tablet.html" "tablet-empty:900x700:tablet.html?empty=1" "tablet-empty-wide:1180x820:tablet.html?empty=1" "channels-tab:900x700:tab.html?tab=channels" "channels-follow:900x700:tab.html?tab=channels&follow=1" "contacts-tab:900x700:tab.html?tab=contacts" "contacts-recommend:900x700:tab.html?tab=contacts&ctab=recommend" "contacts-device:900x700:tab.html?tab=contacts&ctab=device" "dynamics-tab:900x700:tab.html?tab=dynamics" "dynamics-tab-mobile:390x844:tab.html?tab=dynamics&mobile=1" "dynamics-long:390x1400:tab.html?tab=dynamics&mobile=1" "attach-panel:390x844:attach-panel.html" "attach-panel-tablet:900x700:attach-panel.html" "emoji-panel:390x844:emoji-panel.html" "emoji-panel-tablet:900x700:emoji-panel.html" "message-menu:390x844:message-menu.html" "message-menu-tablet:900x700:message-menu.html" "voice-recording:390x844:voice-recording.html" "composer-reply:390x844:composer-reply.html"; do
  IFS=':' read -r name size page <<< "$spec"
  "$CHROME" --no-sandbox --disable-dev-shm-usage --no-zygote \
    --use-gl=swiftshader --disable-vulkan --hide-scrollbars \
    --window-size="$size" \
    --screenshot="$OUT/$name.png" \
    "http://127.0.0.1:$PORT/$page" >/dev/null 2>&1 || echo "FAIL $name"
  echo "shot $name"
done
for spec in "mobile-dark:390x844:mobile.html?dark=1" "mobile-chat-dark:390x844:mobile-chat.html?dark=1" "group-chat-dark:390x844:group-chat.html?dark=1" "tablet-dark:900x700:tablet.html?dark=1" "tablet-empty-dark:900x700:tablet.html?empty=1&dark=1" "tab-channels-dark:900x700:tab.html?tab=channels&dark=1" "channels-follow-dark:900x700:tab.html?tab=channels&follow=1&dark=1" "tab-contacts-dark:900x700:tab.html?tab=contacts&dark=1" "tab-contacts-recommend-dark:900x700:tab.html?tab=contacts&ctab=recommend&dark=1" "tab-contacts-device-dark:900x700:tab.html?tab=contacts&ctab=device&dark=1" "tab-dynamics-dark:900x700:tab.html?tab=dynamics&dark=1" "tab-dynamics-mobile-dark:390x844:tab.html?tab=dynamics&mobile=1&dark=1" "dynamics-long-dark:390x1400:tab.html?tab=dynamics&mobile=1&dark=1" "emoji-panel-dark:390x844:emoji-panel.html?dark=1" "attach-panel-dark:390x844:attach-panel.html?dark=1" "voice-recording-dark:390x844:voice-recording.html?dark=1" "composer-reply-dark:390x844:composer-reply.html?dark=1" "message-menu-dark:390x844:message-menu.html?dark=1"; do
  IFS=':' read -r name size page <<< "$spec"
  "$CHROME" --no-sandbox --disable-dev-shm-usage --no-zygote \
    --use-gl=swiftshader --disable-vulkan --hide-scrollbars \
    --window-size="$size" \
    --screenshot="$OUT/$name.png" \
    "http://127.0.0.1:$PORT/$page" >/dev/null 2>&1 || echo "FAIL $name"
  echo "shot $name"
done
# server left running for csscheck
ls -la "$OUT"
