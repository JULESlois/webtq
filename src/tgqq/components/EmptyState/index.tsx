import {JSX} from 'solid-js';
import styles from './EmptyState.module.scss';

export default function TqEmptyState(props: {
  title: JSX.Element,
  subtitle: JSX.Element
}) {
  return (
    <div class={styles.root}>
      <div class={styles.title}>{props.title}</div>
      <div class={styles.subtitle}>{props.subtitle}</div>
    </div>
  );
}
