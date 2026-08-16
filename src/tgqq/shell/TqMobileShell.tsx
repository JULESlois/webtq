import {createRoot, createSignal, Match, Show, Switch, onMount} from 'solid-js';
import TqBottomNavigation, {TqHomeTab} from '@/tgqq/components/BottomNavigation';
import TqChannelsPage from '@/tgqq/pages/Channels';
import TqContactsPage from '@/tgqq/pages/Contacts';
import TqDynamicsPage from '@/tgqq/pages/Dynamics';
import TqSettingsPage from '@/tgqq/pages/Settings';
import TqProfileDrawer from '@/tgqq/components/ProfileDrawer';
import styles from './TqMobileShell.module.scss';

const [selectedTab, setSelectedTab] = createRoot(() => createSignal<TqHomeTab | 'settings'>('messages'));
const [profileOpen, setProfileOpen] = createRoot(() => createSignal(false));

// QQ9 设置入口：左栏个人卡片（头像行）。点击头像打开 QQ 样式的左滑抽屉，
// 抽屉底部「设置」切到设置页（真机 9.1.65 消息列表顶栏只有加号，无齿轮）。
function injectProfileClick() {
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement | null;
    if(!target) return;
    if(target.closest('.tgqq-profile') && !target.closest('.tgqq-profile-add')) {
      setProfileOpen(true);
    }
  });
}

export default function TqMobileShell() {
  onMount(injectProfileClick);

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
              <TqContactsPage onOpenChannels={() => setSelectedTab('channels')}/>
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
      <TqProfileDrawer
        open={profileOpen()}
        onClose={() => setProfileOpen(false)}
        onSettings={() => {
          setProfileOpen(false);
          setSelectedTab('settings');
        }}
      />
    </div>
  );
}
