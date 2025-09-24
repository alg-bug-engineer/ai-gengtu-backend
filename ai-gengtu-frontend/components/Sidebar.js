// alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/ai-gengtu-frontend/components/Sidebar.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

// 定义功能列表
const features = [
  { title: "AI 梗图", link: "/meme_generator", icon: "/file.svg" },
  { title: "立体雕塑 (开发中)", link: "#", icon: "/globe.svg", disabled: true },
];

export default function Sidebar() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await fetch('http://8.149.232.39:5550/api/logout', { credentials: 'include' });
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // 即使登出接口失败，也强制跳转到登录页
      router.push('/login');
    }
  };

  return (
    <aside className={styles.sidebar}>
      <div>
        <h1 className={styles.sidebarTitle}>AI 创作平台</h1>
        <nav className={styles.featureNav}>
          {features.map((feature) => (
            <Link key={feature.title} href={feature.disabled ? "#" : feature.link}>
              <a className={`${styles.featureLink} ${router.pathname === feature.link ? styles.activeLink : ''} ${feature.disabled ? styles.disabledLink : ''}`}>
                <img src={feature.icon} alt={`${feature.title} icon`} className={styles.featureIcon} />
                {feature.title}
              </a>
            </Link>
          ))}
        </nav>
      </div>

      <button onClick={handleLogout} className={styles.logoutButton}>
        登出
      </button>
    </aside>
  );
}