import {createRoot, createSignal, Match, Show, Switch, onMount} from 'solid-js';
import TqBottomNavigation, {TqHomeTab} from '@/tgqq/components/BottomNavigation';
import TqChannelsPage from '@/tgqq/pages/Channels';
import TqContactsPage from '@/tgqq/pages/Contacts';
import TqDynamicsPage from '@/tgqq/pages/Dynamics';
import TqSettingsPage from '@/tgqq/pages/Settings';
import styles from './TqMobileShell.module.scss';

const [selectedTab, setSelectedTab] = createRoot(() => createSignal<TqHomeTab | 'settings'>('messages'));

// QQ9 设置入口：左栏个人卡片（头像行）右侧的齿轮按钮。侧栏是上游 DOM，
// 由 shell 挂载时注入按钮，点击切到设置页。
function injectProfileGear() {
  const profile = document.querySelector('#column-left .tgqq-profile');
  if(!profile || profile.querySelector('.tq-profile-gear')) return;
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'tq-profile-gear';
  btn.setAttribute('aria-label', '设置');
  btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.5 5.5l-1.7 1.7M7.2 16.8l-1.7 1.7M18.5 18.5l-1.7-1.7M7.2 7.2 5.5 5.5"/></svg>';
  btn.addEventListener('click', () => setSelectedTab('settings'));
  profile.append(btn);
}

export default function TqMobileShell() {
  onMount(injectProfileGear);

  const isMessagesTab = () => selectedTab() === 'messages';

  return (
    <div class={styles.root}>
      <Show when={!isMessagesTab()}>
        <div class={selectedTab() === 'settings' ? `${styles.pages} ${styles.pagesFull}` : styles.pages}>
          <Switch>
            <Match when={selectedTab() === 'channels'}>
              <TqChannelsPage/>
            </Match>
            <Match when={selectedTab() === 'contacts'}>
              <TqContactsPage/>
            </Match>
            <Match when={selectedTab() === 'dynamics'}>
              <TqDynamicsPage/>
            </Match>
            <Match when={selectedTab() === 'settings'}>
              <TqSettingsPage onBack={() => setSelectedTab('messages')}/>
            </Match>
          </Switch>
        </div>
      </Show>
      <Show when={selectedTab() !== 'settings'}>
        <TqBottomNavigation selected={selectedTab()} onSelect={setSelectedTab}/>
      </Show>
    </div>
  );
}
