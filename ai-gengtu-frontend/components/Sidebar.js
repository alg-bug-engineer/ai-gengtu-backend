// alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/ai-gengtu-frontend/components/Sidebar.js
import { useRouter } from 'next/router';
import Link from 'next/link';
import styles from '../styles/Home.module.css';

// 更新功能列表，激活“立体雕塑”
const features = [
  { title: "AI 梗图", link: "/meme_generator", icon: "/file.svg" },
  { title: "立体雕塑", link: "/figurine_generator", icon: "/globe.svg", disabled: false },
];

export default function Sidebar() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/logout`, { credentials: 'include' });
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      router.push('/login');
    }
  };

  return (
    <aside className={styles.sidebar}>
      <div>
        <h1 className={styles.sidebarTitle}>AI 创作平台</h1>
        <nav className={styles.featureNav}>
          {features.map((feature) => (
            <Link
              key={feature.title}
              href={feature.disabled ? "#" : feature.link}
              className={`${styles.featureLink} ${router.pathname === feature.link ? styles.activeLink : ''} ${feature.disabled ? styles.disabledLink : ''}`}
              aria-disabled={feature.disabled}
              onClick={(e) => feature.disabled && e.preventDefault()}
            >
              <img src={feature.icon} alt={`${feature.title} icon`} className={styles.featureIcon} />
              {feature.title}
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