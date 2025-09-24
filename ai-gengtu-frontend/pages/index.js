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
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
        if (userRes.ok) {
          setIsLoggedIn(true);
        } else {
          setIsLoggedIn(false);
          router.push('/login');
        }
      } catch (err) {
        console.error('Fetch error during login status check:', err);
        setIsLoggedIn(false);
        router.push('/login');
      }
    };
    checkLoginStatus();
  }, [router]);

  if (!isLoggedIn) {
    return null;
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>功能列表 - AI 梗图生成器</title>
        <meta name="description" content="AI 梗图生成器应用功能列表" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>选择一个功能</h1>
        <div className={styles.featureGrid}>
          <FeatureCard
            title="AI 梗图生成器"
            description="输入一个谜底，让AI为你创作有趣的看图猜谜梗图。"
            link="/meme_generator"
            icon="/file.svg"
          />
        </div>
      </main>
    </div>
  );
}