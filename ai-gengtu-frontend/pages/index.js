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

  useEffect(() => {
    // 登录后直接重定向到梗图生成器页面
    const checkLoginStatusAndRedirect = async () => {
      try {
        const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
        if (userRes.ok) {
          // 如果已登录，直接跳转到梗图生成器页面
          router.replace('/meme_generator');
        } else {
          // 如果未登录，则跳转到登录页
          router.push('/login');
        }
      } catch (err) {
        console.error('Failed to check login status:', err);
        router.push('/login');
      }
    };
    checkLoginStatusAndRedirect();
  }, [router]);

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