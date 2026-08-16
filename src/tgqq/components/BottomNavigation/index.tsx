import {For, Show} from 'solid-js';
import classNames from '@helpers/string/classNames';
import {i18n} from '@lib/langPack';
import lang from '@/lang';
import styles from './BottomNavigation.module.scss';

export type TqHomeTab = 'messages' | 'channels' | 'contacts' | 'dynamics';

// QQ9 底部导航：极细线性图标（1.5px stroke），语义 = 气泡/井号/人形/时钟。
function TqNavIcon({kind}: {kind: TqHomeTab}) {
  const common = {
    width: 22,
    height: 22,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    'stroke-width': 1.5,
    'stroke-linecap': 'round' as const,
    'stroke-linejoin': 'round' as const
  };
  switch(kind) {
    case 'messages':
      return (
        <svg {...common}><path d="M4 5.5h16a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H11l-4.6 3.6V17.5H4A1.5 1.5 0 0 1 2.5 16V7A1.5 1.5 0 0 1 4 5.5z"/></svg>
      );
    case 'contacts':
      return (
        <svg {...common}><circle cx="12" cy="7.5" r="3.8"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/></svg>
      );
    case 'dynamics':
      return (
        <svg {...common}><path d="M5.5 21V3.5"/><path d="M5.5 4.5c3.5-1.8 7 1.6 11-.2v8.4c-4 1.8-7.5-1.6-11 .2z"/></svg>
      );
  }
}

// QQ9.1.65 real bottom nav has exactly three tabs (消息/联系人/动态);
// Telegram channels are reached from the contacts page (我的频道 entry).
const items: {tab: TqHomeTab, labelKey: keyof typeof lang}[] = [
  {tab: 'messages', labelKey: 'Tgqq.Tab.Messages'},
  {tab: 'contacts', labelKey: 'Tgqq.Tab.Contacts'},
  {tab: 'dynamics', labelKey: 'Tgqq.Tab.Dynamics'}
];

export default function TqBottomNavigation(props: {
  selected: TqHomeTab | 'settings',
  onSelect: (tab: TqHomeTab | 'settings') => void
}) {
  return (
    <nav class={styles.root} aria-label="TGQQ home">
      <For each={items}>
        {(item) => (
          <button
            class={classNames(styles.item, props.selected === item.tab && styles.itemSelected)}
            type="button"
            aria-label={lang[item.labelKey] as string}
            aria-current={props.selected === item.tab ? 'page' : undefined}
            onClick={() => props.onSelect(item.tab)}
          >
            <span class={styles.iconWrap}>
              <TqNavIcon kind={item.tab}/>
              <Show when={item.tab === 'dynamics'}>
                <i class={styles.dot} aria-hidden="true"/>
              </Show>
            </span>
            <span>{i18n(item.labelKey)}</span>
          </button>
        )}
      </For>
    </nav>
  );
}
