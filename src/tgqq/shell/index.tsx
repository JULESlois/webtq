import {render} from 'solid-js/web';
import appImManager from '@lib/appImManager';
import mediaSizes from '@helpers/mediaSizes';
import {tqFlags} from '@/tgqq/config/flags';
import TqMobileShell from './TqMobileShell';

let rootEl: HTMLDivElement | undefined;
let initialized = false;

const SKIN_CLASSES: {flag: boolean, className: string}[] = [
  {flag: tqFlags.dialogSkin, className: 'tq-dialog-skin'},
  {flag: tqFlags.chatHeader, className: 'tq-chat-header'},
  {flag: tqFlags.chatBubbles, className: 'tq-chat-bubbles'},
  {flag: tqFlags.chatComposer, className: 'tq-chat-composer'}
];

function updateShellVisibility() {
  if(!rootEl) return;

  // <600px: phone shell covers the full viewport and only shows on the
  // chatlist tab. >=600px: QQ-tablet structure — the shell (bottom nav +
  // tab pages) is pinned to the left home column and always visible, with
  // the chat rendered as the independent right-hand panel.
  const tablet = !mediaSizes.isMobile;
  const visible = tqFlags.shell &&
    (tablet || document.body.classList.contains('is-left-column-shown'));

  rootEl.classList.toggle('tq-shell-active', visible);
  document.body.classList.toggle('tq-shell-on', visible);
}

function updateSkinState() {
  const tablet = !mediaSizes.isMobile;
  for(const {flag, className} of SKIN_CLASSES) {
    document.body.classList.toggle(className, flag);
  }
  document.body.classList.toggle('tq-tablet', tqFlags.tablet && tablet);
}

export function initTgqq() {
  if(initialized) return;
  initialized = true;

  const pageChatsEl = document.getElementById('page-chats');
  if(!pageChatsEl) return;

  document.body.classList.add('is-tgqq');
  rootEl = document.createElement('div');
  rootEl.classList.add('tq-shell');
  pageChatsEl.append(rootEl);
  render(() => <TqMobileShell/>, rootEl);

  const onStateChange = () => {
    updateShellVisibility();
    updateSkinState();
  };

  appImManager.addEventListener('tab_changing', onStateChange);
  mediaSizes.addEventListener('changeScreen', onStateChange);
  mediaSizes.addEventListener('resize', onStateChange);

  onStateChange();
}
