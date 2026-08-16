import {For, Show, createSignal} from 'solid-js';
import {i18n} from '@lib/langPack';
import styles from './Contacts.module.scss';
import TqTabHeader from '@/tgqq/components/TqTabHeader';

type Contact = {
  name: string;
  sub: string;
  gradient: string;
  badge?: string;
  online?: boolean;
};

type Section = {
  title: string;
  items: Contact[];
};

const friends: Contact[] = [
  {name: '林晚晴', sub: '手机在线', gradient: 'linear-gradient(135deg,#12b7f5,#1296db)', online: true},
  {name: '陈默', sub: '3G 在线', gradient: 'linear-gradient(135deg,#ff9a56,#ff6a3d)', online: true},
  {name: '周子昂', sub: '离线', gradient: 'linear-gradient(135deg,#9b59b6,#8e44ad)'},
  {name: '苏小满', sub: '离线', gradient: 'linear-gradient(135deg,#e91e63,#c2185b)'},
  {name: '沈亦舟', sub: 'WiFi 在线', gradient: 'linear-gradient(135deg,#ff9800,#f57c00)', online: true},
  {name: '郑一鸣', sub: '离线', gradient: 'linear-gradient(135deg,#8bc34a,#689f38)'}
];

const groupChats: Contact[] = [
  {name: '产品讨论组', sub: '12 人', gradient: 'linear-gradient(135deg,#7ed321,#4caf50)'},
  {name: '前端交流群', sub: '86 人', gradient: 'linear-gradient(135deg,#00bcd4,#0097a7)'},
  {name: '周末爬山小队', sub: '8 人', gradient: 'linear-gradient(135deg,#e91e63,#c2185b)'}
];

const multiChats: Contact[] = [
  {name: '四人开黑群', sub: '4 人', gradient: 'linear-gradient(135deg,#607d8b,#455a64)'},
  {name: '图书馆自习室', sub: '6 人', gradient: 'linear-gradient(135deg,#9c27b0,#7b1fa2)'}
];

const recommends: Contact[] = [
  {name: '顾南星', sub: '共同好友 3 人 · 喜欢摄影', gradient: 'linear-gradient(135deg,#12b7f5,#1296db)'},
  {name: '许一诺', sub: '通讯录好友 · 来自手机通讯录', gradient: 'linear-gradient(135deg,#ff9a56,#ff6a3d)'},
  {name: '陆之遥', sub: '共同群聊：前端交流群', gradient: 'linear-gradient(135deg,#9b59b6,#8e44ad)'}
];

const devices = [
  {name: '我的手机', sub: '当前设备 · 在线', icon: 'phone'},
  {name: '我的电脑', sub: '上次登录：3 天前', icon: 'pc'},
  {name: '我的平板', sub: '上次登录：上周', icon: 'pad'}
];

const groupFriends: Contact[] = [
  {name: '林晚晴', sub: '手机在线', gradient: 'linear-gradient(135deg,#12b7f5,#1296db)', online: true},
  {name: '陈默', sub: '3G 在线', gradient: 'linear-gradient(135deg,#ff9a56,#ff6a3d)', online: true},
  {name: '周子昂', sub: '离线', gradient: 'linear-gradient(135deg,#9b59b6,#8e44ad)'},
  {name: '沈亦舟', sub: 'WiFi 在线', gradient: 'linear-gradient(135deg,#ff9800,#f57c00)', online: true}
];

const groupSections: Section[] = [
  {title: '特别关心', items: []},
  {title: '我的好友', items: groupFriends},
  {title: '我的群聊', items: groupChats},
  {title: '多人聊天', items: multiChats}
];

const tabs = [
  {key: 'recommend', label: '推荐'},
  {key: 'friends', label: '好友'},
  {key: 'group', label: '分组'},
  {key: 'groupChat', label: '群聊'},
  {key: 'device', label: '设备'}
] as const;

type TabKey = typeof tabs[number]['key'];

const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

function ContactRow(props: {c: Contact}) {
  const c = props.c;
  return (
    <div class={styles.row}>
      <div class={styles.avatarWrap}>
        <div class={styles.rowAvatar} style={{background: c.gradient}}>{c.name.slice(0, 1)}</div>
        <Show when={c.online}>
          <i class={styles.onlineDot} aria-hidden="true"/>
        </Show>
      </div>
      <div class={styles.rowMeta}>
        <div class={styles.rowName}>{c.name}</div>
        <div class={styles.rowSub}>{c.sub}</div>
      </div>
      <Show when={c.badge}>
        <span class={styles.badge}>{c.badge}</span>
      </Show>
    </div>
  );
}

function RecommendRow(props: {c: Contact}) {
  const c = props.c;
  return (
    <div class={styles.row}>
      <div class={styles.avatarWrap}>
        <div class={styles.rowAvatar} style={{background: c.gradient}}>{c.name.slice(0, 1)}</div>
      </div>
      <div class={styles.rowMeta}>
        <div class={styles.rowName}>{c.name}</div>
        <div class={styles.rowSub}>{c.sub}</div>
      </div>
      <button type="button" class={styles.addBtn}>添加</button>
    </div>
  );
}

function DeviceIcon(props: {kind: string}) {
  return (
    <span class={styles.deviceIcon}>
      {props.kind === 'phone' && (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M10.8 18.5h2.4"/></svg>
      )}
      {props.kind === 'pc' && (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="12" rx="2"/><path d="M9 20.5h6M12 16.5v4"/></svg>
      )}
      {props.kind === 'pad' && (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4.5" y="3.5" width="15" height="17" rx="2"/><path d="M10.5 18h3"/></svg>
      )}
    </span>
  );
}

function DeviceRow(props: {name: string, sub: string, icon: string}) {
  return (
    <div class={styles.row}>
      <DeviceIcon kind={props.icon}/>
      <div class={styles.rowMeta}>
        <div class={styles.rowName}>{props.name}</div>
        <div class={styles.rowSub}>{props.sub}</div>
      </div>
      <span class={styles.rowArrow}>›</span>
    </div>
  );
}

function ChannelsRow(props: {onOpen?: () => void}) {
  return (
    <button type="button" class={styles.channelsRow} onClick={props.onOpen}>
      <span class={styles.channelsIcon}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M9 3.5 6.5 20.5"/><path d="M17.5 3.5 15 20.5"/><path d="M4 9h17"/><path d="M3 15h17"/></svg>
      </span>
      <span class={styles.channelsMeta}>
        <span class={styles.channelsName}>我的频道</span>
        <span class={styles.channelsSub}>进入频道广场</span>
      </span>
      <span class={styles.channelsArrow}>›</span>
    </button>
  );
}

export default function TqContactsPage(props: {onOpenChannels?: () => void}) {
  const [activeTab, setActiveTab] = createSignal<TabKey>('group');
  const [collapsed, setCollapsed] = createSignal<Set<number>>(new Set([0]));

  const toggleGroup = (idx: number) => {
    setCollapsed(prev => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx); else next.add(idx);
      return next;
    });
  };

  const onlineCount = (items: Contact[]) => items.filter((c) => c.online).length;

  return (
    <div class={styles.root}>
      <TqTabHeader searchPlaceholder={i18n('Tgqq.Contacts.Search')} title="联系人" showStatus={false} compact addIcon="personAdd"/>

      <div class={styles.quickNav}>
        <div class={styles.quickNavItem}>
          <span class={styles.quickNavText}>{i18n('Tgqq.Contacts.NewFriends')}</span>
          <span class={styles.quickNavRight}>
            <span class={styles.quickNavBadge}>1</span>
            <span class={styles.quickNavArrow}>›</span>
          </span>
        </div>
        <div class={styles.quickNavItem}>
          <span class={styles.quickNavText}>群通知</span>
          <span class={styles.quickNavArrow}>›</span>
        </div>
      </div>

      <ChannelsRow onOpen={props.onOpenChannels}/>

      <div class={styles.tabs} role="tablist">
        <For each={tabs}>
          {(t) => (
            <button
              type="button"
              role="tab"
              aria-selected={activeTab() === t.key}
              class={activeTab() === t.key ? `${styles.tab} ${styles.tabActive}` : styles.tab}
              onClick={() => setActiveTab(t.key)}
            >{t.label}</button>
          )}
        </For>
      </div>

      <div class={styles.content}>
        <Show when={activeTab() === 'friends'}>
          <section class={styles.section}>
            <div class={styles.list}>
              <For each={friends}>{(c) => <ContactRow c={c}/>}</For>
            </div>
          </section>
        </Show>

        <Show when={activeTab() === 'group'}>
          <For each={groupSections}>
            {(sec, i) => (
              <section class={styles.section}>
                <div class={styles.sectionHeader} onClick={() => toggleGroup(i())}>
                  <span class={styles.sectionHeaderLeft}>
                    <i class={collapsed().has(i()) ? styles.sectionArrow : `${styles.sectionArrow} ${styles.sectionArrowOpen}`} aria-hidden="true"/>
                    <span class={styles.sectionName}>{sec.title}</span>
                  </span>
                  <span class={styles.sectionCount}>{onlineCount(sec.items)}/{sec.items.length}</span>
                </div>
                <Show when={!collapsed().has(i())}>
                  <div class={styles.list}>
                    <For each={sec.items}>{(c) => <ContactRow c={c}/>}</For>
                  </div>
                </Show>
              </section>
            )}
          </For>
        </Show>

        <Show when={activeTab() === 'groupChat'}>
          <section class={styles.section}>
            <div class={styles.list}>
              <For each={[...groupChats, ...multiChats]}>{(c) => <ContactRow c={c}/>}</For>
            </div>
          </section>
        </Show>

        <Show when={activeTab() === 'recommend'}>
          <section class={styles.section}>
            <div class={styles.sectionLabel}>推荐联系人</div>
            <div class={styles.list}>
              <For each={recommends}>{(c) => <RecommendRow c={c}/>}</For>
            </div>
          </section>
        </Show>

        <Show when={activeTab() === 'device'}>
          <section class={styles.section}>
            <div class={styles.sectionLabel}>我的设备</div>
            <div class={styles.list}>
              <For each={devices}>{(d) => <DeviceRow name={d.name} sub={d.sub} icon={d.icon}/>}</For>
            </div>
          </section>
        </Show>
      </div>

      <div class={styles.indexBar} aria-hidden="true">
        <For each={letters}>{(l) => <span class={styles.indexLetter}>{l}</span>}</For>
      </div>
    </div>
  );
}
