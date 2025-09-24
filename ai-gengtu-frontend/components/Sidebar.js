import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

const features = [
  { title: "梗图生成器", link: "/meme_generator", icon: "/file.svg" },
  // 未来可以在这里添加更多功能
];

export default function Sidebar() {
  const [history, setHistory] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  const handleLogout = async () => {
    await fetch('http://8.149.232.39:5550/api/logout', { credentials: 'include' });
    router.push('/login');
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
        if (userRes.ok) {
          setIsLoggedIn(true);
          const historyRes = await fetch('http://8.149.232.39:5550/api/history', { credentials: 'include' });
          if (historyRes.ok) {
            const historyData = await historyRes.json();
            setHistory(historyData);
          }
        } else {
          setIsLoggedIn(false);
          router.push('/login');
        }
      } catch (err) {
        console.error('Failed to fetch history:', err);
        // 这里不进行重定向，由 Layout 组件统一处理未登录情况
      }
    };
    fetchHistory();
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

      <div className={styles.historyContainer}>
        <h3 className={styles.historyTitle}>历史记录</h3>
        <ul className={styles.historyList}>
          {history.length > 0 ? (
            history.map((item) => (
              <li key={item.id} className={styles.historyItem}>
                <Link href={`/meme_generator?historyId=${item.id}`} className={styles.historyLink}>
                  <img src={`http://8.149.232.39:5550${item.image_url}`} alt={item.riddle_answer} className={styles.historyImageSmall} />
                  <span>{item.riddle_answer}</span>
                </Link>
              </li>
            ))
          ) : (
            <p className={styles.noHistoryText}>暂无历史记录。</p>
          )}
        </ul>
      </div>

      <button onClick={handleLogout} className={styles.logoutButton}>
        登出
      </button>
    </aside>
  );
}