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
    const checkLogin = async () => {
      console.log('useEffect: Starting login status check.');
      try {
        const res = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
        console.log('API call to /api/user finished with status:', res.status);
        if (res.ok) {
          const data = await res.json();
          console.log('User is logged in. User info:', data);
          setIsLoggedIn(true);
          setCredits(data.credits);
        } else {
          console.log('User is not logged in. Status:', res.status, 'Redirecting to login page.');
          setIsLoggedIn(false);
          router.push('/login');
        }
      } catch (err) {
        console.error('Fetch user info error during useEffect:', err);
        setIsLoggedIn(false);
        router.push('/login');
      }
    };
    checkLogin();
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('handleSubmit: Form submission started.');
    setLoading(true);
    setError(null);
    setImageUrl(null);

    if (!answer) {
      console.log('Validation failed: Answer is empty.');
      setError('请输入一个谜底词语。');
      setLoading(false);
      return;
    }

    console.log('Answer to be submitted:', answer);
    try {
      const response = await fetch('http://8.149.232.39:5550/api/generate_meme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer }),
        credentials: 'include'
      });

      console.log('API call to /api/generate_meme finished with status:', response.status);

      if (response.status === 402) {
        const errorData = await response.json();
        console.error('API Error (402):', errorData.message);
        throw new Error(errorData.message);
      }
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData.message || 'API 请求失败，请检查后端服务。');
        throw new Error(errorData.message || 'API 请求失败，请检查后端服务。');
      }

      const imageBlob = await response.blob();
      console.log('Image blob received successfully. Blob size:', imageBlob.size, 'bytes.');
      const objectURL = URL.createObjectURL(imageBlob);
      setImageUrl(objectURL);
      console.log('Image URL created:', objectURL);

      // 生成成功后，重新获取用户额度
      console.log('Generation successful. Fetching updated user credits.');
      const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
      if (userRes.ok) {
        const userData = await userRes.json();
        setCredits(userData.credits);
        console.log('Updated credits fetched successfully. New credits:', userData.credits);
      } else {
        console.error('Failed to fetch updated credits. Status:', userRes.status);
      }

    } catch (err) {
      console.error('An error occurred during meme generation:', err);
      setError(err.message);
    } finally {
      console.log('handleSubmit: Function finished. Setting loading to false.');
      setLoading(false);
    }
  };
  
  if (!isLoggedIn) {
    console.log('Not logged in, rendering null.');
    return null;
  }

  console.log('Rendering HomePage component. Credits:', credits);

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
            onChange={(e) => {
              setAnswer(e.target.value);
              console.log('Input value changed:', e.target.value);
            }}
            placeholder="例如：东施效颦"
            disabled={loading || (credits !== null && credits <= 0)}
          />
          <button type="submit" className={styles.button} disabled={loading || (credits !== null && credits <= 0)}>
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