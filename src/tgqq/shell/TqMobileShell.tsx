import {createRoot, createSignal, Match, Show, Switch} from 'solid-js';
import TqBottomNavigation, {TqHomeTab} from '@/tgqq/components/BottomNavigation';
import TqChannelsPage from '@/tgqq/pages/Channels';
import TqContactsPage from '@/tgqq/pages/Contacts';
import TqDynamicsPage from '@/tgqq/pages/Dynamics';
import styles from './TqMobileShell.module.scss';

const [selectedTab, setSelectedTab] = createRoot(() => createSignal<TqHomeTab>('messages'));

export default function TqMobileShell() {
  const isMessagesTab = () => selectedTab() === 'messages';

  return (
    <div class={styles.root}>
      <Show when={!isMessagesTab()}>
        <div class={styles.pages}>
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
          </Switch>
        </div>
      </Show>
      <TqBottomNavigation selected={selectedTab()} onSelect={setSelectedTab}/>
    </div>
  );
}
