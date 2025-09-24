import Head from 'next/head';
import Sidebar from './Sidebar';
import styles from '../styles/Home.module.css';

export default function Layout({ children }) {
  return (
    <>
      <Head>
        <title>AI 创作平台</title>
        <meta name="description" content="AI 梗图生成器及更多功能" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.appContainer}>
        <Sidebar />
        <main className={styles.mainContent}>
          {children}
        </main>
      </div>
    </>
  );
}