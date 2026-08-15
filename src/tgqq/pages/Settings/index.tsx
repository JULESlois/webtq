import {Show, For} from 'solid-js';
import classNames from '@helpers/string/classNames';
import type {JSXElement} from 'solid-js';
import styles from './Settings.module.scss';

// QQ9 设置页：通用（004）/ 辅助功能（005）两个子屏，共用导航头与列表行样式。

const ICON = {
  stroke: 'currentColor',
  fill: 'none',
  'stroke-width': 1.6,
  'stroke-linecap': 'round' as const,
  'stroke-linejoin': 'round' as const
};

type Row = {
  icon: string;
  label: string;
  value?: string;
  chevron?: boolean;
  toggle?: boolean;
  toggleOn?: boolean;
  badge?: string;
};

type Group = {rows: Row[], desc?: string};

const svgIcons: Record<string, JSXElement> = {
  monitor: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><rect x="3" y="4.5" width="18" height="12.5" rx="2"/><path d="M9.5 20.5h5M12 17v3.5"/></svg>,
  moon: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M20 13.2A8 8 0 0 1 10.8 4a8 8 0 1 0 9.2 9.2z"/></svg>,
  tower: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M6.5 21V11a5.5 5.5 0 0 1 11 0v10"/><path d="M4 21h16"/><path d="M12 11v3.5"/><path d="M9.5 14.5h5"/></svg>,
  fontA: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M5 19.5 11 4.5h2l6 15"/><path d="M8.5 14h7"/></svg>,
  storage: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v11a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 17.5z"/><path d="M4 9.5h16"/><path d="M8 13.5h.01M11.5 13.5h.01"/></svg>,
  clock: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2.2"/></svg>,
  download: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M12 3.5v11"/><path d="M7.5 10.5 12 15l4.5-4.5"/><path d="M4.5 19.5h15"/></svg>,
  bubble: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M4 5.5h16a1.5 1.5 0 0 1 1.5 1.5v8a1.5 1.5 0 0 1-1.5 1.5H11l-4.5 3.5V16.5H4A1.5 1.5 0 0 1 2.5 15V7A1.5 1.5 0 0 1 4 5.5z"/></svg>,
  enter: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M9.5 4.5H18a1.5 1.5 0 0 1 1.5 1.5v8A1.5 1.5 0 0 1 18 15.5H4.5"/><path d="M8 11.5 4.5 15 8 18.5"/></svg>,
  eye: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg>,
  avatar: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><circle cx="12" cy="8" r="3.5"/><path d="M5 19.5c.9-3.2 3.4-4.8 7-4.8s6.1 1.6 7 4.8"/></svg>,
  undo: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M9.5 5.5 4.5 10.5l5 5"/><path d="M4.5 10.5H15a4.5 4.5 0 0 1 0 9h-2.5"/></svg>,
  phone: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M6.5 3.5h3l1.5 4.5-2.2 1.6a12.5 12.5 0 0 0 5.6 5.6l1.6-2.2 4.5 1.5v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.5 5.7a2 2 0 0 1 2-2.2z"/></svg>,
  star: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="m12 3.5 2.5 5.2 5.7.7-4.2 4 1.1 5.6-5.1-2.8-5.1 2.8 1.1-5.6-4.2-4 5.7-.7z"/></svg>,
  smile: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><circle cx="12" cy="12" r="8.5"/><path d="M8.5 10h.01M15.5 10h.01"/><path d="M8.5 13.5a4 4 0 0 0 7 0"/></svg>,
  dui: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><rect x="3.5" y="4" width="17" height="16" rx="3"/><path d="M8.5 10.5h.01M15.5 10.5h.01"/><path d="M8.5 14a4 4 0 0 0 7 0"/></svg>,
  tag: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M5 4.5h14v15l-7-3.2-7 3.2z"/></svg>,
  menu: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M4 6.5h16"/><path d="M4 12h16"/><path d="M4 17.5h16"/></svg>,
  wave: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><path d="M4 12h2l2-6 3 12 2.5-9 1.5 3h3"/></svg>,
  grid: <svg width="22" height="22" viewBox="0 0 24 24" {...ICON}><circle cx="5" cy="5" r="1.8"/><circle cx="12" cy="5" r="1.8"/><circle cx="19" cy="5" r="1.8"/><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/><circle cx="5" cy="19" r="1.8"/><circle cx="12" cy="19" r="1.8"/><circle cx="19" cy="19" r="1.8"/></svg>
};

function RowItem(props: {row: Row}) {
  const r = props.row;
  return (
    <div class={styles.row}>
      <span class={styles.rowIcon}>{svgIcons[r.icon]}</span>
      <span class={styles.rowLabel}>
        {r.label}
        <Show when={r.badge}><em class={styles.badge}>{r.badge}</em></Show>
      </span>
      <Show when={r.value}><span class={styles.rowValue}>{r.value}</span></Show>
      <Show when={r.toggle}>
        <button
          type="button"
          class={classNames(styles.toggle, r.toggleOn && styles.toggleOn)}
          aria-pressed={!!r.toggleOn}
          aria-label={r.label}
        ><i/></button>
      </Show>
      <Show when={r.chevron}>
        <svg class={styles.rowArrow} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 5.5 16 12l-6.5 6.5"/></svg>
      </Show>
    </div>
  );
}

const GENERAL: Group[] = [
  {
    head: '模式选择',
    rows: []
  },
  {
    rows: [
      {icon: 'moon', label: '夜间模式跟随系统', toggle: true, toggleOn: true}
    ]
  },
  {
    rows: [
      {icon: 'tower', label: '使用移动网络改善语音质量', toggle: true, toggleOn: true}
    ],
    desc: 'Wi-Fi下通话效果不佳时，使用移动网络改善语音质量，每分钟流量消耗约1MB。'
  },
  {
    rows: [
      {icon: 'fontA', label: '字体大小', chevron: true}
    ]
  },
  {
    rows: [
      {icon: 'storage', label: '存储空间', value: '聊天记录、文件清理', chevron: true},
      {icon: 'clock', label: '聊天记录设置', chevron: true},
      {icon: 'download', label: '自动下载与保存', chevron: true}
    ]
  },
  {
    rows: [
      {icon: 'bubble', label: '系统通知栏显示QQ图标', toggle: true},
      {icon: 'enter', label: '回车键发送消息', toggle: true},
      {icon: 'eye', label: '使用群文件在线预览服务', toggle: true, toggleOn: true}
    ],
    desc: '开启后支持100MB以下的Office文件在线预览，大于100MB以上的文件需下载后查看。'
  }
];

const ACCESSIBILITY: Group[] = [
  {
    rows: [
      {icon: 'avatar', label: '头像双击动作设置', chevron: true},
      {icon: 'undo', label: '撤回消息设置', chevron: true},
      {icon: 'phone', label: '语音/视频通话设置', chevron: true},
      {icon: 'star', label: '超级QQ秀设置', chevron: true}
    ]
  },
  {
    rows: [
      {icon: 'smile', label: '表情推荐', toggle: true, toggleOn: true},
      {icon: 'dui', label: '怼图', toggle: true, toggleOn: true}
    ]
  },
  {
    rows: [
      {icon: 'tag', label: '彩签设置', chevron: true},
      {icon: 'menu', label: '主页底部导航栏设置', chevron: true},
      {icon: 'wave', label: '语音消息自动转文本(可体验)', badge: 'SVIP', toggle: true},
      {icon: 'grid', label: '更多功能设置', chevron: true}
    ]
  }
];

export default function TqSettingsPage(props: {sub?: 'general' | 'accessibility', onBack?: () => void}) {
  const isAccessibility = () => props.sub === 'accessibility';
  const groups = () => isAccessibility() ? ACCESSIBILITY : GENERAL;

  return (
    <div class={styles.root}>
      <header class={styles.nav}>
        <button type="button" class={styles.back} aria-label="返回" onClick={props.onBack}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 5 8 12l6.5 7"/></svg>
        </button>
        <h1 class={styles.title}>{isAccessibility() ? '辅助功能' : '设置'}</h1>
      </header>
      <div class={styles.content}>
        <Show when={!isAccessibility()}>
          <section class={styles.card}>
            <div class={styles.modeHead}>
              <span class={styles.rowIcon}>{svgIcons.monitor}</span>
              <span class={styles.modeTitle}>模式选择</span>
              <span class={styles.modeMore}>更多模式
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 5.5 16 12l-6.5 6.5"/></svg>
              </span>
            </div>
            <div class={styles.modeGrid}>
              <div class={`${styles.modeCard} ${styles.modeCardSelected}`}>
                <span class={styles.modeCardTitle}>普通模式</span>
                <span class={styles.modeCardSub}>随心使用，畅享装扮。</span>
                <i class={styles.radio} aria-hidden="true">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5 10 17.5 19 7.5"/></svg>
                </i>
              </div>
              <div class={styles.modeCard}>
                <span class={styles.modeCardTitle}>体验模式</span>
                <span class={styles.modeCardSub}>全新设计，全新体验。</span>
                <i class={styles.radio} aria-hidden="true"/>
              </div>
              <div class={styles.modeCard}>
                <span class={styles.modeCardTitle}>青少年模式</span>
                <span class={styles.modeCardSub}>功能管控，守护成长。</span>
                <i class={styles.radio} aria-hidden="true"/>
              </div>
            </div>
          </section>
        </Show>
        <For each={groups()}>
          {(group) => (
            <>
              <section class={styles.card}>
                <For each={group.rows}>
                  {(row) => <RowItem row={row}/>}
                </For>
              </section>
              <Show when={group.desc}><p class={styles.desc}>{group.desc}</p></Show>
            </>
          )}
        </For>
      </div>
    </div>
  );
}
