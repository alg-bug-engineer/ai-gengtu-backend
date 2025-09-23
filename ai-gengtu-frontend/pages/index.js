// pages/index.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function HomePage() {
  const [answer, setAnswer] = useState('');
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [credits, setCredits] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  // 检查登录状态和获取用户额度
  useEffect(() => {
    async function checkLogin() {
      try {
        const res = await fetch('http://localhost:5550/api/user', {credentials: 'include'});
        if (res.ok) {
          const data = await res.json();
          setIsLoggedIn(true);
          setCredits(data.credits);
        } else {
          // 未登录，重定向到登录页
          setIsLoggedIn(false);
          router.push('/login');
        }
      } catch (err) {
        console.error('Fetch user info error:', err);
        setIsLoggedIn(false);
        router.push('/login');
      }
    }
    checkLogin();
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setImageUrl(null);

    if (!answer) {
      setError('请输入一个谜底词语。');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5550/api/generate_meme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer }),
        credentials: 'include'
      });

      if (response.status === 402) {
        const errorData = await response.json();
        throw new Error(errorData.message);
      }
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'API 请求失败，请检查后端服务。');
      }

      const imageBlob = await response.blob();
      const objectURL = URL.createObjectURL(imageBlob);
      setImageUrl(objectURL);

      // 生成成功后，重新获取用户额度
      const userRes = await fetch('http://localhost:5550/api/user', {credentials: 'include'});
      if (userRes.ok) {
        const userData = await userRes.json();
        setCredits(userData.credits);
      }

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // 只有在登录后才渲染主界面
  if (!isLoggedIn) {
    return null;
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>AI 梗图生成器</title>
        <meta name="description" content="用 AI 创作有趣的梗图" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>AI 梗图生成器</h1>
        <p className={styles.description}>
          剩余额度：<span style={{ fontWeight: 'bold' }}>{credits !== null ? credits : '加载中...'}</span>
        </p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <input
            type="text"
            className={styles.input}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="例如：东施效颦"
            disabled={loading || credits <= 0}
          />
          <button type="submit" className={styles.button} disabled={loading || credits <= 0}>
            {loading ? '生成中...' : '生成梗图'}
          </button>
        </form>

        {loading && <p className={styles.status}>正在努力创作中，请稍候...</p>}
        
        {error && <p className={styles.error}>{error}</p>}

        {imageUrl && (
          <div className={styles.resultContainer}>
            <h2>生成的梗图：</h2>
            <img src={imageUrl} alt="Generated meme" className={styles.image} />
            <a href={imageUrl} download="meme.png" className={styles.downloadLink}>
              下载梗图
            </a>
          </div>
        )}
      </main>
    </div>
  );
}