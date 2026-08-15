import {JSX, Show} from 'solid-js';
import styles from './PageContainer.module.scss';

export default function TqPageContainer(props: {
  title?: JSX.Element,
  children: JSX.Element
}) {
  return (
    <div class={styles.root}>
      <Show when={props.title}>
        <header class={styles.header}>{props.title}</header>
      </Show>
      <div class={styles.content}>{props.children}</div>
    </div>
  );
}
