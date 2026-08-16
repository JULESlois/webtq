import {For, Show, createSignal} from 'solid-js';
import styles from './Dynamics.module.scss';

import photo01 from '../../assets/photos/photo01.jpg';
import photo02 from '../../assets/photos/photo02.jpg';
import photo03 from '../../assets/photos/photo03.jpg';
import photo04 from '../../assets/photos/photo04.jpg';
import photo05 from '../../assets/photos/photo05.jpg';
import photo06 from '../../assets/photos/photo06.jpg';
import photo07 from '../../assets/photos/photo07.jpg';
import photo08 from '../../assets/photos/photo08.jpg';
import photo09 from '../../assets/photos/photo09.jpg';
import photo10 from '../../assets/photos/photo10.jpg';
import photo11 from '../../assets/photos/photo11.jpg';
import photo12 from '../../assets/photos/photo12.jpg';

type Post = {
  name: string;
  time: string;
  text: string;
  images: number;
  likes: number;
  comments: number;
  forwards: number;
  gradient: string;
  imgStart: number;
};

const posts: Post[] = [
  {
    name: '林晚晴', time: '10 分钟前', gradient: 'linear-gradient(135deg,#12b7f5,#1296db)', imgStart: 0,
    text: '周末去爬山，有一起的吗？🌄 山顶风景真的绝了，随手一拍都是壁纸。',
    images: 3, likes: 23, comments: 5, forwards: 2
  },
  {
    name: '陈默', time: '1 小时前', gradient: 'linear-gradient(135deg,#ff9a56,#ff6a3d)', imgStart: 4,
    text: '新版原型终于定稿了，感谢大家这几天的反馈！',
    images: 1, likes: 41, comments: 12, forwards: 6
  },
  {
    name: '产品讨论组', time: '2 小时前', gradient: 'linear-gradient(135deg,#7ed321,#4caf50)', imgStart: 0,
    text: '本周周会纪要已同步，重点：v3 排期、灰度方案、下周双周会时间。',
    images: 0, likes: 18, comments: 9, forwards: 4
  },
  {
    name: '沈亦舟', time: '昨天 21:40', gradient: 'linear-gradient(135deg,#ff9800,#f57c00)', imgStart: 3,
    text: '周五晚八点老地方，桌游 + 烤肉，报名接龙走起 🍖',
    images: 9, likes: 35, comments: 20, forwards: 3
  }
];

const PHOTOS = [photo01, photo02, photo03, photo04, photo05, photo06, photo07, photo08, photo09, photo10, photo11, photo12];

const PHOTO_GRADS = [
  'linear-gradient(135deg,#ffd3a5,#fd6585)',
  'linear-gradient(135deg,#a1c4fd,#7aa5f0)',
  'linear-gradient(135deg,#fbc2eb,#a18cd1)',
  'linear-gradient(135deg,#84fab0,#5ecf8a)',
  'linear-gradient(135deg,#f6d365,#fda085)',
  'linear-gradient(135deg,#d4fc79,#96e6a1)'
];

const ENTRIES = [
  {label: '相册', color: '#F0C020', d: 'M4 6h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1Z', d2: 'm4 18 5.2-5.2 3.4 3.4 2.8-2.8L21 18'},
  {label: '说说', color: '#F0C010', d: 'M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5Z', d2: 'M8.5 12h.01M12 12h.01M15.5 12h.01'},
  {label: '游戏中心', color: '#1090E0', d: 'M7 8h10a4 4 0 0 1 4 4v3a3 3 0 0 1-5.2 2L14 15h-4l-1.8 2A3 3 0 0 1 3 15v-3a4 4 0 0 1 4-4Z', d2: 'M7 12h.01M10 13.5h.01M14 13.5h.01M17 12h.01'},
  {label: '小游戏', color: '#2090D0', d: 'M4 20V9l8-6 8 6v11h-5v-6H9v6H4Z', d2: 'M9 9h.01M15 9h.01M12 13v3m-1.5-1.5h3'},
  {label: '农场', color: '#33C77D', d: 'M12 21c-4 0-7-2.7-7-6.5C5 9 9 5.5 12 3c3 2.5 7 6 7 11.5C19 18.3 16 21 12 21Z', d2: 'M12 21c-1.8-1.4-2.7-3.4-2.7-5.7 0-2 .8-3.7 2.7-5.3 1.9 1.6 2.7 3.3 2.7 5.3 0 2.3-.9 4.3-2.7 5.7Z'},
  {label: '购物', color: '#EB6672', d: 'M6 8h12l-1 12H7L6 8Z', d2: 'M9 8a3 3 0 0 1 6 0'},
  {label: '意见反馈', color: '#2496EA', d: 'M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5Z', d2: 'M8.5 12h.01M12 12h.01M15.5 12h.01'},
  {label: '更多', color: '#1F96E8', d: 'M5 12h.01M12 12h.01M19 12h.01'}
];

function ImageGrid(props: {count: number, imgStart: number}) {
  const cells = props.count === 0 ? [] : Array.from({length: props.count});
  return (
    <Show when={cells.length > 0}>
      <div class={props.count === 1 ? styles.imgSingle : props.count === 3 ? styles.imgThree : styles.imgGrid}>
        <For each={cells}>
          {(_, i) => {
            const src = PHOTOS[(props.imgStart + i()) % PHOTOS.length];
            const grad = PHOTO_GRADS[i() % PHOTO_GRADS.length];
            return (
              <div class={styles.imgCell} style={{background: grad}}>
                <img src={src} alt="" loading="lazy"/>
              </div>
            );
          }}
        </For>
      </div>
    </Show>
  );
}

function PostCard(props: {p: Post}) {
  const [liked, setLiked] = createSignal(false);
  const p = props.p;
  return (
    <article class={styles.card}>
      <div class={styles.cardHeader}>
        <div class={styles.cardAvatar} style={{background: p.gradient}}>{p.name.slice(0, 1)}</div>
        <div class={styles.cardMeta}>
          <div class={styles.cardName}>{p.name}</div>
          <div class={styles.cardTime}>{p.time}</div>
        </div>
      </div>
      <div class={styles.cardText}>{p.text}</div>
      <ImageGrid count={p.images} imgStart={p.imgStart}/>
      <div class={styles.cardActions}>
        <button
          type="button"
          class={liked() ? `${styles.actionBtn} ${styles.actionBtnActive}` : styles.actionBtn}
          onClick={() => setLiked(!liked())}
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill={liked() ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.6-9.2-8.6C1.2 8.6 3 5.5 6.2 5.5c2 0 3.3 1.1 4.2 2.4l1.6 2.1 1.6-2.1c.9-1.3 2.2-2.4 4.2-2.4 3.2 0 5 3.1 3.2 5.9C19 15.4 12 20 12 20z"/></svg>
          <span>{p.likes + (liked() ? 1 : 0)}</span>
        </button>
        <button type="button" class={styles.actionBtn}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.4 8.9 8.9 0 0 1-3.4-.7L3 20.5l1.3-4.1a8 8 0 0 1-.8-3.4A8.4 8.4 0 0 1 12 4.5a8.4 8.4 0 0 1 9 7z"/></svg>
          <span>{p.comments}</span>
        </button>
        <button type="button" class={styles.actionBtn}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M16 6l-4-4-4 4"/><path d="M12 2v13"/></svg>
          <span>{p.forwards}</span>
        </button>
      </div>
    </article>
  );
}


/* ---- Round 23: QQ9 dynamics hub lower modules ---- */

const PARTNERS = [
  {title: '梦搭子', sub: '专属战绩'},
  {title: '王者搭子', sub: '同步王者战绩'},
  {title: '学习搭子', sub: '一起进步'},
  {title: '运动搭子', sub: '一起自律'}
];

function DynamicsPartners() {
  return (
    <div class={styles.partners}>
      <For each={PARTNERS}>
        {(pt) => (
          <div class={styles.partnerItem}>
            <div class={styles.partnerTitle}>{pt.title}</div>
            <div class={styles.partnerSub}>{pt.sub}</div>
            <button type="button" class={styles.partnerAdd} aria-label={`添加${pt.title}`}>+</button>
          </div>
        )}
      </For>
    </div>
  );
}

function DynamicsBadges() {
  return (
    <div class={styles.badges}>
      <div class={styles.badgesHead}>
        <span class={styles.badgesTitle}>互动标识</span>
        <span class={styles.badgesCount}>3/23</span>
        <span class={styles.badgesMore}>›</span>
      </div>
      <div class={styles.badgesRow}>
        <div class={styles.badgeItem} style={{background: 'linear-gradient(135deg,#a78bfa,#4ecdc4)'}}>
          <svg class={styles.badgeSvg} viewBox="0 0 24 24"><rect x="10.8" y="1.6" width="2.4" height="3.2" rx="1.1" fill="#fff"/><rect x="10.8" y="4.2" width="2.4" height="7.4" rx="1.1" fill="#fff"/><path d="M12 11.6c-4.2 0-6.9 2.7-6.9 5.6 0 2.9 2.7 5 6.9 5s6.9-2.1 6.9-5S16.2 11.6 12 11.6z" fill="#fff"/><path d="M9.6 14.6c.6-.5 1.4-.8 2.4-.8" stroke="#a78bfa" stroke-width="1.1" fill="none" stroke-linecap="round"/></svg>
          <i class={styles.badgeQ}>Q</i>
        </div>
        <div class={styles.badgeItem} style={{background: 'linear-gradient(135deg,#4ecdc4,#44a8b3)'}}>
          <svg class={styles.badgeSvg} viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.2s6 6.3 6 10.3A6 6 0 0 1 12 19.5a6 6 0 0 1-6-6c0-4 6-10.3 6-10.3z"/></svg>
        </div>
        <div class={styles.badgeItem} style={{background: 'linear-gradient(135deg,#ffe066,#ffb300)'}}>
          <svg class={styles.badgeSvg} viewBox="0 0 24 24" fill="none" stroke="none"><ellipse cx="12" cy="6.5" rx="3" ry="4.2" fill="#fff" opacity="0.95"/><ellipse cx="17.2" cy="9" rx="3" ry="4.2" transform="rotate(72 12 12)" fill="#ffb3d1" opacity="0.95"/><ellipse cx="15.2" cy="15.4" rx="3" ry="4.2" transform="rotate(144 12 12)" fill="#fff" opacity="0.95"/><ellipse cx="8.8" cy="15.4" rx="3" ry="4.2" transform="rotate(216 12 12)" fill="#ffb3d1" opacity="0.95"/><ellipse cx="6.8" cy="9" rx="3" ry="4.2" transform="rotate(288 12 12)" fill="#fff" opacity="0.95"/><circle cx="12" cy="12" r="2.4" fill="#fff3c4"/></svg>
        </div>
        <div class={styles.badgeItem} style={{background: 'var(--tq-surface-secondary)'}}>
          <span class={styles.badgePlaceholder}>20个</span>
          <span class={styles.badgePlaceholderSub}>待点亮</span>
        </div>
      </div>
    </div>
  );
}

function SectionLabel(props: {text: string}) {
  return <div class={styles.sectionLabel}>{props.text}</div>;
}

function LuckyCharCard() {
  return (
    <div class={styles.assetCard}>
      <div class={styles.assetIcon}>
        <svg viewBox="0 0 24 24" fill="none" stroke="#c4a35a" stroke-width="2.6" stroke-linecap="round"><path d="M8 5l8 14M16 5L8 19"/></svg>
      </div>
      <div class={styles.assetMeta}>
        <div class={styles.assetTitle}>幸运字符</div>
        <div class={styles.assetSub}>抽取专属字符</div>
      </div>
      <span class={styles.assetCta}>开启 〉</span>
    </div>
  );
}

function NovelCreatureCard() {
  return (
    <div class={styles.assetCard}>
      <div class={styles.assetIcon} style={{background: 'linear-gradient(135deg,#f8d3e8,#cfe9ff)'}}>
        <svg class={styles.creatureSvg} viewBox="0 0 48 48" fill="none">
          <circle cx="17" cy="25" r="9" fill="#ff9ecb"/>
          <circle cx="31" cy="25" r="9" fill="#7ec8ff"/>
          <circle cx="14.4" cy="22.6" r="1.6" fill="#333"/>
          <circle cx="19.6" cy="22.6" r="1.6" fill="#333"/>
          <circle cx="28.4" cy="22.6" r="1.6" fill="#333"/>
          <circle cx="33.6" cy="22.6" r="1.6" fill="#333"/>
          <path d="M14.6 27.4c1.5 1.4 3.3 2 5.4 2s3.9-.6 5.4-2" stroke="#333" stroke-width="1.4" stroke-linecap="round"/>
          <path d="M28.6 27.4c1.5 1.4 3.3 2 5.4 2s3.9-.6 5.4-2" stroke="#333" stroke-width="1.4" stroke-linecap="round"/>
        </svg>
      </div>
      <div class={styles.assetMeta}>
        <div class={styles.assetTitle}>解锁聊天新玩法</div>
        <div class={styles.assetSub}>我是超级可爱的新奇物种</div>
      </div>
      <span class={styles.assetCta}>去养成 〉</span>
    </div>
  );
}

function DnaSection() {
  return (
    <div class={styles.dna}>
      <SectionLabel text="我们的DNA"/>
      <div class={styles.dnaDivider}/>
    </div>
  );
}

function DynamicsHeader() {
  return (
    <header class={styles.header}>
      <span class={styles.headerTitle}>动态</span>
      <div class={styles.headerActions}>
        <button type="button" class={styles.headerIcon} aria-label="通知">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M18 9.5a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6"/><path d="M10 19a2.2 2.2 0 0 0 4 0"/></svg>
        </button>
        <button type="button" class={styles.headerIcon} aria-label="设置">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.5 5.5l-1.7 1.7M7.2 16.8l-1.7 1.7M18.5 18.5l-1.7-1.7M7.2 7.2 5.5 5.5"/></svg>
        </button>
      </div>
    </header>
  );
}

function WeatherBanner() {
  return (
    <button type="button" class={styles.weather}>
      <span class={styles.weatherIcon}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 3v2.2M12 18.8V21M3 12h2.2M18.8 12H21M5.6 5.6l1.6 1.6M16.8 16.8l1.6 1.6M18.4 5.6l-1.6 1.6M7.2 16.8l-1.6 1.6"/></svg>
      </span>
      <span class={styles.weatherMeta}>
        <span class={styles.weatherTitle}>分享此刻天空</span>
        <span class={styles.weatherSub}>记录周末心情</span>
      </span>
      <span class={styles.weatherArrow}>›</span>
    </button>
  );
}

function CoupleSpace() {
  return (
    <button type="button" class={styles.couple}>
      <span class={styles.coupleIcon}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M12 20s-7-4.6-9.2-8.6C1.2 8.6 3 5.5 6.2 5.5c2 0 3.3 1.1 4.2 2.4l1.6 2.1 1.6-2.1c.9-1.3 2.2-2.4 4.2-2.4 3.2 0 5 3.1 3.2 5.9C19 15.4 12 20 12 20z"/></svg>
      </span>
      <span class={styles.coupleMeta}>
        <span class={styles.coupleTitle}>亲密空间</span>
        <span class={styles.coupleSub}>只属于两个人的小空间</span>
      </span>
      <span class={styles.coupleArrow}>›</span>
    </button>
  );
}

function DynamicsProfileCard() {
  return (
    <div class={styles.profileCard}>
      <div class={styles.profileAvatar}>我</div>
      <div class={styles.profileMeta}>
        <div class={styles.profileName}>我</div>
        <div class={styles.profileSign}>活着就好 ›</div>
      </div>
      <span class={styles.profileArrow}>&#8250;</span>
    </div>
  );
}

function DynamicsEntries() {
  return (
    <div class={styles.entries}>
      <For each={ENTRIES}>
        {(e) => (
          <div class={styles.entryItem}>
            <span class={styles.entryIcon} style={{color: e.color}}>
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d={e.d}/>{e.d2 ? <path d={e.d2}/> : null}</svg>
            </span>
            <span class={styles.entryLabel}>{e.label}</span>
          </div>
        )}
      </For>
    </div>
  );
}

export default function TqDynamicsPage() {
  return (
    <div class={styles.root}>
      <DynamicsHeader/>
      <DynamicsProfileCard/>

      <div class={styles.content}>
        <DynamicsEntries/>
        <WeatherBanner/>
        <CoupleSpace/>

        <DynamicsPartners/>
        <DynamicsBadges/>

        <SectionLabel text="我们的幸运物种"/>
        <LuckyCharCard/>

        <SectionLabel text="新奇物种"/>
        <NovelCreatureCard/>

        <DnaSection/>

        <div class={styles.feedTitle}>好友动态</div>
        <For each={posts}>
          {(p) => <PostCard p={p}/>}
        </For>
      </div>
    </div>
  );
}
