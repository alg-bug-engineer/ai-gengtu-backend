import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

const features = [
  { title: "梗图生成器", link: "/meme_generator", icon: "/file.svg" },
  // 未来可以在这里添加更多功能
];

export default function Sidebar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  const handleLogout = async () => {
    await fetch('http://8.149.232.39:5550/api/logout', { credentials: 'include' });
    router.push('/login');
  };

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
        console.error('Failed to check login status:', err);
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
    <aside className={styles.sidebar}>
      <h2 className={styles.sidebarTitle}>功能列表</h2>
      <nav className={styles.featureNav}>
        {features.map((feature) => (
          <Link key={feature.link} href={feature.link} className={styles.featureLink}>
            <img src={feature.icon} alt={feature.title} className={styles.featureIcon} />
            {feature.title}
          </Link>
        ))}
      </nav>

      <button onClick={handleLogout} className={styles.logoutButton}>
        登出
      </button>
    </aside>
  );
}