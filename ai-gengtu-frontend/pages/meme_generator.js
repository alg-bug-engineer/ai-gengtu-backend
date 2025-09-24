import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function MemeGeneratorPage() {
  const [answer, setAnswer] = useState('');
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [credits, setCredits] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedSize, setSelectedSize] = useState('vertical');
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
        if (userRes.ok) {
          const userData = await userRes.json();
          setCredits(userData.credits);

          const historyRes = await fetch('http://8.149.232.39:5550/api/history', { credentials: 'include' });
          if (historyRes.ok) {
            const historyData = await historyRes.json();
            setHistory(historyData);
          } else {
            console.error('Failed to fetch history:', historyRes.status);
          }
        }
      } catch (err) {
        console.error('Failed to fetch data:', err);
      }
    };
    fetchData();
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
      const response = await fetch('http://8.149.232.39:5550/api/generate_meme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer, selectedSize }),
        credentials: 'include'
      });

      // 优化错误处理，根据状态码返回更友好的提示
      if (response.status === 402) {
        // 402 错误表示额度不足
        const errorData = await response.json();
        throw new Error(errorData.message || '您的生成额度已用完。');
      }
      
      if (!response.ok) {
        // 其他非OK状态码，返回通用错误信息
        throw new Error('梗图生成失败，请稍后再试。');
      }

      const imageBlob = await response.blob();
      const objectURL = URL.createObjectURL(imageBlob);
      setImageUrl(objectURL);

      // 生成成功后，重新获取用户额度
      const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
      if (userRes.ok) {
        const userData = await userRes.json();
        setCredits(userData.credits);
      } else {
        setCredits(0);
      }
    } catch (err) {
      console.error('An error occurred during meme generation:', err);
      setError(err.message || '哎呀，出了点小问题，请稍后再试。');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className={styles.memeGeneratorPage}>
      <Head>
        <title>AI 梗图生成器</title>
      </Head>

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
          disabled={loading || (credits !== null && credits <= 0)}
        />
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

      {imageUrl && (
        <div className={styles.resultContainer}>
          <h2>最新生成的梗图：</h2>
          <img src={imageUrl} alt="Generated meme" className={styles.image} />
          <a href={imageUrl} download="meme.png" className={styles.downloadLink}>
            下载梗图
          </a>
        </div>
      )}

      {history.length > 0 && (
        <div className={styles.historyContainer}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', textAlign: 'center' }}>你的历史梗图</h2>
          <div className={styles.historyGrid}>
            {history.map((item) => (
              <div key={item.id} className={styles.historyItem}>
                <img 
                  src={`http://8.149.232.39:5550${item.image_url}`} 
                  alt={item.riddle_answer} 
                  className={styles.historyImage} 
                />
                <p className={styles.historyPrompt}>{item.riddle_answer}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}