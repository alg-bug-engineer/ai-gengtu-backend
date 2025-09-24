import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

const FeatureCard = ({ title, description, link, icon }) => (
  <Link href={link} className={styles.featureCard}>
    <div className={styles.cardContent}>
      <img src={icon} alt={`${title} icon`} className={styles.cardIcon} />
      <h3 className={styles.cardTitle}>{title}</h3>
      <p className={styles.cardDescription}>{description}</p>
    </div>
  </Link>
);

export default function FeaturesPage() {
  const router = useRouter();

  // 登录检查和历史记录获取已移至 Sidebar
  // 这里只负责页面内容的展示
  
  return (
    <div className={styles.featurePageContainer}>
      <Head>
        <title>功能列表 - AI 创作平台</title>
      </Head>
      <h1 className={styles.title}>选择一个功能</h1>
      <div className={styles.featureGrid}>
        <FeatureCard
          title="AI 梗图生成器"
          description="输入一个谜底，让AI为你创作有趣的看图猜谜梗图。"
          link="/meme_generator"
          icon="/file.svg"
        />
      </div>
    </div>
  );
}