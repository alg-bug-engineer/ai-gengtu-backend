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
  const [history, setHistory] = useState([]); // 新增状态来存储历史记录
  const [selectedSize, setSelectedSize] = useState('vertical'); // 默认尺寸为'vertical'
  const router = useRouter();


  // 检查登录状态和获取用户额度及历史记录
  useEffect(() => {
    const checkLoginAndFetchData = async () => {
      console.log('useEffect: Starting login status check and data fetch.');
      try {
        const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
        console.log('API call to /api/user finished with status:', userRes.status);
        if (userRes.ok) {
          const userData = await userRes.json();
          console.log('User is logged in. User info:', userData);
          setIsLoggedIn(true);
          setCredits(userData.credits);

          // 成功登录后，立即获取历史记录
          const historyRes = await fetch('http://8.149.232.39:5550/api/history', { credentials: 'include' });
          if (historyRes.ok) {
            const historyData = await historyRes.json();
            setHistory(historyData);
            console.log('History data fetched successfully.', historyData);
          } else {
            console.error('Failed to fetch history. Status:', historyRes.status);
          }

        } else {
          console.log('User is not logged in. Redirecting to login page.');
          setIsLoggedIn(false);
          router.push('/login');
        }
      } catch (err) {
        console.error('Fetch error during useEffect:', err);
        setIsLoggedIn(false);
        router.push('/login');
      }
    };
    checkLoginAndFetchData();
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
        body: JSON.stringify({ answer, selectedSize }), // 传递新参数
        credentials: 'include'
      });

      console.log('API call to /api/generate_meme finished with status:', response.status);

      if (response.status === 402) {
        const errorData = await response.json();
        console.error('API Error (402):', errorData.message);
        throw new Error(errorData.message);
      }
      const data = await response.json();
      if (!response.ok) {
        // const errorData = await response.json();
        console.error('API Error:', errorData.message || 'API 请求失败，请检查后端服务。');
        setError(data.message || 'API 请求失败，请检查后端服务。');
        throw new Error(data.message || 'API 请求失败');
        // throw new Error(errorData.message || 'API 请求失败，请检查后端服务。');
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
      // setError(err.message);
      setError('哎呀，出了点小问题，请稍后再试。');
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

        {/* 确保您的 form 元素在此处 */}
        <form className={styles.form} onSubmit={handleSubmit}>
          <input
            type="text"
            className={styles.input}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="例如：东施效颦"
            disabled={loading || (credits !== null && credits <= 0)}
          />
          {/* 新增尺寸选择器 */}
            <select
              value={selectedSize}
              onChange={(e) => setSelectedSize(e.target.value)}
              disabled={loading || (credits !== null && credits <= 0)}
              style={{ width: '100%', marginBottom: '1rem', padding: '0.75rem', fontSize: '1rem' }}
            >
              <option value="vertical">竖屏（1024x1920）</option>
              <option value="horizontal">横屏（1920x1024）</option>
              <option value="square">正方形（1024x1024）</option>
            </select>
          <button type="submit" className={styles.button} disabled={loading || (credits !== null && credits <= 0)}>
            {loading ? '生成中，您可以离开，稍后在返回本页面查看结果即可...' : '生成梗图'}
          </button>
        </form>

        {loading && <p className={styles.status}>正在努力创作中，请稍候...</p>}
        
        {error && <p className={styles.error}>{error}</p>}

        {/* 当前生成结果展示区 */}
        {imageUrl && (
          <div className={styles.resultContainer}>
            <h2>最新生成的梗图：</h2>
            <img src={imageUrl} alt="Generated meme" className={styles.image} />
            <a href={imageUrl} download="meme.png" className={styles.downloadLink}>
              下载梗图
            </a>
          </div>
        )}

        {/* 历史记录展示区 */}
        {history.length > 0 && (
          <div className={styles.historyContainer}>
            <h2>你的历史梗图</h2>
            <div className={styles.historyGrid}>
              {history.map((item) => (
                <div key={item.id} className={styles.historyItem}>
                  <img 
                    src={`http://8.149.232.39:5550${item.image_url}`} // 优化：拼接完整的后端 URL
                    alt={item.riddle_answer} 
                    className={styles.historyImage} 
                  />
                  <p className={styles.historyPrompt}>{item.riddle_answer}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
