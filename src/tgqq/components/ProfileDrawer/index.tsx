import {For, Show} from 'solid-js';
import styles from './ProfileDrawer.module.scss';

// QQ 9.1.65 左滑「我的」抽屉（ref qq9-mobile3/007/008）：
// 蓝色渐变头部（关闭 + 大头像 + 昵称 + QQ号 + 个性签名）
// + 白色圆角菜单卡（8 项：相册/收藏/文件/钱包/财富小金库/会员中心/个性装扮/免流量）
// + 底部操作栏（设置/夜间/定位）。

const MENU = [
  {label: '相册', icon: 'M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z', color: '#F8C315'},
  {label: '收藏', icon: 'M12 3l2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1L3.2 9.4l6.1-.9L12 3Z', color: '#1194EC'},
  {label: '文件', icon: 'M6 3h8l5 5v13H6V3Zm7 0v6h6', color: '#07C160'},
  {label: '钱包', icon: 'M3 7h18v11H3V7Zm0 5h18M7 16h5', color: '#FA8C16'},
  {label: '财富小金库', icon: 'M12 3l2.5 5 5.5.8-4 3.9.9 5.5L12 15.9 7.1 18.2l.9-5.5-4-3.9L9.5 8 12 3Z', color: '#B7893F'},
  {label: '会员中心', icon: 'M12 3l3 4.5L20 9l-3.5 4.5L17 20l-5-2.8L7 20l.5-6.5L4 9l5-.5L12 3Z', color: '#E14E9B'},
  {label: '个性装扮', icon: 'M5 4h14v5H5V4Zm0 6h14v5H5v-5Zm0 6h8v4H5v-4Zm11 1v4m-2-2h4', color: '#8B5CF6'},
  {label: '免流量', icon: 'M12 3a9 9 0 1 0 9 9c0-1.2-.2-2.3-.7-3.3L12 12V3Zm0 0a9 9 0 0 1 9 9', color: '#00B8D4'}
];

export default function ProfileDrawer(props: {open: boolean, onClose: () => void, onSettings: () => void}) {
  return (
    <Show when={props.open}>
      <div class={styles.backdrop} onClick={props.onClose}/>
      <div class={styles.panel} role="dialog" aria-label="个人主页">
        <div class={styles.header}>
          <div class={styles.headerBar}>
            <button type="button" class={styles.checkin}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="m9.5 15 2 2 3.5-3.8"/></svg>
              <span>打卡</span>
            </button>
            <div class={styles.headerBarRight}>
              <button type="button" class={styles.statusBtn} aria-label="状态">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8.5 14.5c.9 1.2 2.1 1.8 3.5 1.8s2.6-.6 3.5-1.8"/><path d="M9 10h.01M15 10h.01"/></svg>
              </button>
              <button type="button" class={styles.close} onClick={props.onClose} aria-label="关闭">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
              </button>
            </div>
          </div>
          <div class={styles.avatar}>我</div>
          <div class={styles.meta}>
            <div class={styles.nameRow}>
              <span class={styles.name}>我</span>
              <button type="button" class={styles.switchAccount}>切换账号 &#9662;</button>
            </div>
            <div class={styles.qq}>QQ号：10001</div>
            <div class={styles.sign}>这个人很懒，什么都没留下</div>
          </div>
          <span class={styles.chevron}>&#8250;</span>
        </div>

        <div class={styles.card}>
          <For each={MENU}>
            {(m) => (
              <button type="button" class={styles.row}>
                <span class={styles.rowIcon} style={{color: m.color}}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d={m.icon}/></svg>
                </span>
                <span class={styles.rowLabel}>{m.label}</span>
                <span class={styles.rowArrow}>&#8250;</span>
              </button>
            )}
          </For>
        </div>

        <div class={styles.footer}>
          <div class={styles.footerBar}>
            <button type="button" class={styles.footerItem} onClick={props.onSettings}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.5 5.5l-1.7 1.7M7.2 16.8l-1.7 1.7M18.5 18.5l-1.7-1.7M7.2 7.2 5.5 5.5"/></svg>
              <span>设置</span>
            </button>
            <button type="button" class={styles.footerItem}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5Z"/></svg>
              <span>夜间</span>
            </button>
            <button type="button" class={styles.footerItem}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-5.3-6.5-10A6.5 6.5 0 0 1 12 4.5 6.5 6.5 0 0 1 18.5 11c0 4.7-6.5 10-6.5 10Z"/><circle cx="12" cy="11" r="2.3"/></svg>
              <span>扬中</span>
            </button>
          </div>
          <span class={styles.version}>WebQQ 9.1.65</span>
        </div>
      </div>
    </Show>
  );
}
