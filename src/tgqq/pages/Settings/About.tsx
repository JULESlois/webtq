import type {JSXElement} from 'solid-js';
import styles from './About.module.scss';

// QQ9 设置-关于QQ 页（002）
// 结构：粉蓝渐变 hero（白色返回箭头 + 半透明企鹅 + 渐变 QQ9 字标）
//      → 白色圆角卡片（当前版本/版本更新/功能介绍/官网/帮助/反馈）
//      → 卡片外底部：服务协议·隐私政策·客服热线·版权·ICP 备案

const ICON = {
  stroke: 'currentColor',
  fill: 'none',
  'stroke-width': 1.7,
  'stroke-linecap': 'round' as const,
  'stroke-linejoin': 'round' as const
};

type AboutRow = {
  icon: JSXElement;
  label: string;
  value?: string;
};

const ROWS: AboutRow[] = [
  {
    icon: <svg width="15" height="15" viewBox="0 0 24 24" {...ICON}><path d="M5 5.5h14a1.5 1.5 0 0 1 1.5 1.5v10a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 17V7A1.5 1.5 0 0 1 5 5.5z"/><path d="M3.5 9.5h17M8 5.5V3.8M16 5.5V3.8"/></svg>,
    label: '当前版本',
    value: 'V 9.0.0.14110'
  },
  {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" {...ICON}><circle cx="12" cy="12" r="8.5"/><path d="M12 8.2v7.6"/><path d="M8.2 12h7.6"/></svg>,
    label: '版本更新',
    value: '已是最新版本'
  },
  {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" {...ICON}><path d="M8.5 6.5H18a1.5 1.5 0 0 1 1.5 1.5v10a1.5 1.5 0 0 1-1.5 1.5H6A1.5 1.5 0 0 1 4.5 18V9"/><path d="M4.5 6.5h3M8 3.5v6"/></svg>,
    label: '功能介绍'
  },
  {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" {...ICON}><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5a4.2 4.2 0 0 1 1.9 8"/><path d="M12 15.5a2.4 2.4 0 0 0 2.3-2.7c-.2-1.9-1.9-2.4-2.3-5.3-.4 2.9-2.1 3.4-2.3 5.3a2.4 2.4 0 0 0 2.3 2.7z"/></svg>,
    label: '官网'
  },
  {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" {...ICON}><circle cx="12" cy="12" r="8.5"/><path d="M9.8 10.2a2.4 2.4 0 1 1 4.4 1.3c-.7 1.2-2.2 1.5-2.2 2.9"/><path d="M12 17.4h.01"/></svg>,
    label: '帮助'
  },
  {
    icon: <svg width="16" height="16" viewBox="0 0 24 24" {...ICON}><rect x="4" y="4" width="16" height="16" rx="2.5"/><path d="M9.5 9.8a2.6 2.6 0 0 1 5 .8c0 1.8-2.4 2.2-2.4 3.4"/><path d="M12 16.6h.01"/></svg>,
    label: '反馈'
  }
];

function Penguin() {
  return (
    <svg class={styles.penguin} viewBox="0 0 120 138" aria-hidden="true">
      <defs>
        <linearGradient id="tq-penguin" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#fff" stop-opacity="0.95"/>
          <stop offset="1" stop-color="#fff" stop-opacity="0.55"/>
        </linearGradient>
      </defs>
      <path
        fill="url(#tq-penguin)"
        d="M60 6c-19 0-33 13-35 29-11 4-19 14-19 25 0 11 7 19 16 24l-4 38c-1 6 3 10 9 10h66c6 0 10-4 9-10l-4-38c9-5 16-13 16-24 0-11-8-21-19-25-2-16-16-29-35-29z"
      />
      <ellipse cx="60" cy="98" rx="23" ry="20" fill="#fff" opacity="0.35"/>
      <circle cx="47" cy="52" r="4.5" fill="#fff" opacity="0.8"/>
      <circle cx="73" cy="52" r="4.5" fill="#fff" opacity="0.8"/>
      <path d="M55 63.5h10l-5 7.5z" fill="#fff" opacity="0.75"/>
    </svg>
  );
}

export default function TqAboutPage(props: {onBack?: () => void}) {
  return (
    <div class={styles.root}>
      <div class={styles.hero}>
        <button type="button" class={styles.back} aria-label="返回" onClick={props.onBack}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 5 8 12l6.5 7"/></svg>
        </button>
        <div class={styles.logo}>
          <Penguin/>
          <div class={styles.wordmark}>QQ9</div>
        </div>
      </div>

      <div class={styles.card}>
        {ROWS.map((row) => (
          <div class={styles.row}>
            <span class={styles.rowIcon}>{row.icon}</span>
            <span class={styles.rowLabel}>{row.label}</span>
            {row.value && <span class={styles.rowValue}>{row.value}</span>}
            {!row.value && (
              <svg class={styles.rowArrow} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 5.5 16 12l-6.5 6.5"/></svg>
            )}
          </div>
        ))}
      </div>

      <footer class={styles.footer}>
        <p><span class={styles.qnt}>基于</span><svg class={styles.qntBadge} width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.2 13.6 4.6v6.8L8 14.8 2.4 11.4V4.6z" fill="#f7c948" fill-opacity="0.25" stroke="#d9a52e" stroke-width="1"/><text x="8" y="10.6" text-anchor="middle" font-size="6.2" font-weight="700" fill="#b07d1a">QNT</text></svg><span>QQNT 技术架构</span></p>
        <p><a href="#">服务协议</a><span class={styles.footerSep}>|</span><a href="#">隐私政策</a></p>
        <p>客户服务热线 400 670 0700</p>
        <p>Copyright © 2009-2023 Tencent. All Rights Reserved.</p>
        <p>ICP 备案号 粤B2-20090059-1622A ›</p>
      </footer>
    </div>
  );
}
