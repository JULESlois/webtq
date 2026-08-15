import {Show} from 'solid-js';
import styles from './TqTabHeader.module.scss';

type Props = {
  searchPlaceholder: string;
  // Contacts-page variant: title + person-add icon instead of name/status + "+".
  title?: string;
  showStatus?: boolean;
  addIcon?: 'plus' | 'personAdd';
  compact?: boolean;
};

// QQ9 tab-page topbar: profile row (avatar + name + online status + "+")
// + search pill, geometry matches the messages-page header (same height).
// Contacts page uses the QQ9 contacts header variant (avatar + title + person-add).
export default function TqTabHeader(props: Props) {
  const title = () => props.title ?? '我';
  const showStatus = () => props.showStatus ?? true;
  const addIcon = () => props.addIcon ?? 'plus';
  const cls = () => [
    styles.header,
    props.compact ? styles.headerCompact : '',
  ].filter(Boolean).join(' ');

  return (
    <header class={cls()}>
      <div class={styles.profileRow}>
        <div class={styles.avatar}>我</div>
        <div class={styles.meta}>
          <div class={styles.name}>{title()}</div>
          <Show when={showStatus()}>
            <div class={styles.status}><i class={styles.dot}/><span>手机在线 · WiFi</span></div>
          </Show>
        </div>
        <Show when={addIcon() === 'plus'}>
          <button type="button" class={styles.add} aria-label="添加"/>
        </Show>
        <Show when={addIcon() === 'personAdd'}>
          <button type="button" class={styles.addIcon} aria-label="添加联系人">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="9" cy="8" r="3.5"/>
              <path d="M3.5 19c.8-3.2 2.8-4.8 5.5-4.8s4.7 1.6 5.5 4.8"/>
              <path d="M18.5 9v6M15.5 12h6"/>
            </svg>
          </button>
        </Show>
      </div>
      <div class={styles.search}>
        <svg class={styles.searchIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <span class={styles.searchPlaceholder}>{props.searchPlaceholder}</span>
      </div>
    </header>
  );
}
