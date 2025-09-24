// alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/ai-gengtu-frontend/pages/index.js
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function HomePage() {
  return (
    <div className={styles.welcomeContainer}>
      <Head>
        <title>欢迎 - AI 创作平台</title>
      </Head>
      <h1 className={styles.welcomeTitle}>欢迎光临</h1>
      <p className={styles.welcomeText}>请从左侧选择一个功能开始您的创作之旅。</p>
    </div>
  );
}