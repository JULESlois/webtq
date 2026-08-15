import {For, Show, createSignal} from 'solid-js';
import {i18n} from '@lib/langPack';
import styles from './Channels.module.scss';
import TqTabHeader from '@/tgqq/components/TqTabHeader';

type Channel = {
  id: string;
  name: string;
  desc: string;
  subs: string;
  gradient: string;
  tag?: string;
};

const recommended: Channel[] = [
  {id: 'tengxun', name: '腾讯新闻', desc: '每天 3 分钟，读懂世界', subs: '128万', gradient: 'linear-gradient(135deg,#ff7a59,#ff3d68)'},
  {id: 'keji', name: '科技前沿', desc: 'AI / 芯片 / 新能源', subs: '56万', gradient: 'linear-gradient(135deg,#12b7f5,#0a5f94)'},
  {id: 'yingshi', name: '影视热播', desc: '新片速递与深度影评', subs: '89万', gradient: 'linear-gradient(135deg,#9b59b6,#6c3483)'},
  {id: 'youxi', name: '游戏圈', desc: '开黑组队与攻略分享', subs: '210万', gradient: 'linear-gradient(135deg,#27ae60,#1e8449)'}
];

const industries: Channel[] = [
  {id: 'zixun', name: '科技资讯', desc: '互联网大厂动态与行业观察', subs: '45.2万', gradient: 'linear-gradient(135deg,#4fc3f7,#1565c0)'},
  {id: 'caijing', name: '财经观察', desc: '宏观经济与投资理财', subs: '38.7万', gradient: 'linear-gradient(135deg,#ffb74d,#e65100)'},
  {id: 'zhichang', name: '职场成长', desc: '简历面试与职场干货', subs: '21.5万', gradient: 'linear-gradient(135deg,#81c784,#2e7d32)'}
];

const interests: Channel[] = [
  {id: 'sheying', name: '摄影漫游', desc: '街头摄影与调色教程', subs: '12.3万', gradient: 'linear-gradient(135deg,#ba68c8,#6a1b9a)'},
  {id: 'diantai', name: '深夜电台', desc: '助眠音乐与睡前故事', subs: '9.8万', gradient: 'linear-gradient(135deg,#4dd0e1,#006064)'}
];

const small: Channel[] = [
  {id: 'duli', name: '独立游戏开发', desc: '聊聊引擎、玩法与发行', subs: '3.2万', gradient: 'linear-gradient(135deg,#ff8a80,#b71c1c)', tag: '常逛'},
  {id: 'shouchong', name: '手冲咖啡研究所', desc: '豆子、器具与冲煮方案', subs: '2.6万', gradient: 'linear-gradient(135deg,#a1887f,#4e342e)', tag: '常逛'}
];

const allChannels: Channel[] = [...recommended, ...industries, ...interests, ...small];

function ChannelRow(props: {channel: Channel, followed: boolean, onToggleFollow: () => void}) {
  const c = props.channel;
  return (
    <div class={styles.row}>
      <div class={styles.rowAvatar} style={{background: c.gradient}}>{c.name.slice(0, 1)}</div>
      <div class={styles.rowMeta}>
        <div class={styles.rowName}>{c.name}</div>
        <div class={styles.rowDesc}>{c.desc}</div>
      </div>
      <div class={styles.rowSubs}>{c.subs}人关注</div>
      <button
        type="button"
        class={props.followed ? `${styles.followBtn} ${styles.followBtnActive}` : styles.followBtn}
        onClick={props.onToggleFollow}
      >{props.followed ? '已关注' : '+ 关注'}</button>
    </div>
  );
}

export default function TqChannelsPage() {
  const [tab, setTab] = createSignal<'recommend' | 'follow'>('recommend');
  const [followedIds, setFollowedIds] = createSignal<Set<string>>(new Set());

  const toggleFollow = (id: string) => {
    setFollowedIds((prev) => {
      const next = new Set(prev);
      if(next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const followedChannels = () => allChannels.filter((c) => followedIds().has(c.id));

  return (
    <div class={styles.root}>
      <TqTabHeader searchPlaceholder={i18n('Tgqq.Channels.Search')}/>

      <div class={styles.tabs} role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab() === 'recommend'}
          class={tab() === 'recommend' ? `${styles.tab} ${styles.tabActive}` : styles.tab}
          onClick={() => setTab('recommend')}
        >{i18n('Tgqq.Channels.Recommend')}</button>
        <button
          type="button"
          role="tab"
          aria-selected={tab() === 'follow'}
          class={tab() === 'follow' ? `${styles.tab} ${styles.tabActive}` : styles.tab}
          onClick={() => setTab('follow')}
        >{i18n('Tgqq.Channels.Follow')}</button>
      </div>

      <Show when={tab() === 'recommend'} fallback={
        <div class={styles.content}>
          <Show when={followedChannels().length > 0} fallback={
            <div class={styles.empty}>
              <div class={styles.emptyIcon}>＋</div>
              <div class={styles.emptyTitle}>{i18n('Tgqq.Channels.FollowEmpty')}</div>
              <div class={styles.emptySub}>{i18n('Tgqq.Channels.FollowEmptySub')}</div>
            </div>
          }>
            <div class={styles.list} style={{marginTop: '14px'}}>
              <For each={followedChannels()}>
                {(c) => <ChannelRow channel={c} followed={followedIds().has(c.id)} onToggleFollow={() => toggleFollow(c.id)}/>}
              </For>
            </div>
          </Show>
        </div>
      }>
        <div class={styles.content}>
          <section class={styles.section}>
            <h2 class={styles.sectionTitle}>{i18n('Tgqq.Channels.Recommended')}</h2>
            <div class={styles.cards}>
              <For each={recommended}>
                {(c) => <RecommendCard channel={c} followed={followedIds().has(c.id)} onToggleFollow={() => toggleFollow(c.id)}/>}
              </For>
            </div>
          </section>

          <section class={styles.section}>
            <h2 class={styles.sectionTitle}>{i18n('Tgqq.Channels.Industries')}</h2>
            <div class={styles.list}>
              <For each={industries}>{(c) => <ChannelRow channel={c} followed={followedIds().has(c.id)} onToggleFollow={() => toggleFollow(c.id)}/>}</For>
            </div>
          </section>

          <section class={styles.section}>
            <h2 class={styles.sectionTitle}>{i18n('Tgqq.Channels.Interests')}</h2>
            <div class={styles.list}>
              <For each={interests}>{(c) => <ChannelRow channel={c} followed={followedIds().has(c.id)} onToggleFollow={() => toggleFollow(c.id)}/>}</For>
            </div>
          </section>

          <section class={styles.section}>
            <h2 class={styles.sectionTitle}>{i18n('Tgqq.Channels.Small')}</h2>
            <div class={styles.list}>
              <For each={small}>{(c) => <ChannelRow channel={c} followed={followedIds().has(c.id)} onToggleFollow={() => toggleFollow(c.id)}/>}</For>
            </div>
          </section>
        </div>
      </Show>
    </div>
  );
}

function RecommendCard(props: {channel: Channel, followed: boolean, onToggleFollow: () => void}) {
  const c = props.channel;
  return (
    <div class={styles.card}>
      <div class={styles.cardCover} style={{background: c.gradient}}>
        <span class={styles.cardLetter}>{c.name.slice(0, 1)}</span>
      </div>
      <div class={styles.cardName}>{c.name}</div>
      <div class={styles.cardDesc}>{c.desc}</div>
      <div class={styles.cardFooter}>
        <span class={styles.cardSubs}>{c.subs}人关注</span>
        <button
          type="button"
          class={props.followed ? `${styles.followBtn} ${styles.followBtnActive}` : styles.followBtn}
          onClick={props.onToggleFollow}
        >{props.followed ? '已关注' : '+ 关注'}</button>
      </div>
    </div>
  );
}
