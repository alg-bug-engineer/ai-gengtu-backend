// alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/ai-gengtu-frontend/pages/meme_generator.js
import { useState, useEffect, useCallback } from 'react';
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

  const fetchUserData = useCallback(async () => {
    try {
      const userRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/user`, { credentials: 'include' });
      if (userRes.ok) {
        const userData = await userRes.json();
        setCredits(userData.credits);
      } else {
        // 如果获取用户信息失败，可能 session 过期，跳转到登录页
        window.location.href = '/login';
      }
    } catch (err) {
      console.error('Failed to fetch user data:', err);
      setError('无法加载用户信息，请检查网络连接。');
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const historyRes = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/history`, { credentials: 'include' });
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setHistory(historyData);
      } else {
        console.error('Failed to fetch history:', historyRes.statusText);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  }, []);


  useEffect(() => {
    fetchUserData();
    fetchHistory();
  }, [fetchUserData, fetchHistory]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) {
      setError('请输入一个有效的谜底。');
      return;
    }
    setLoading(true);
    setError(null);
    setImageUrl(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/generate_meme`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer, selectedSize }),
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `生成失败 (状态码: ${response.status})`);
      }

      const imageBlob = await response.blob();
      const objectURL = URL.createObjectURL(imageBlob);
      setImageUrl(objectURL);

      // 操作成功后，刷新额度和历史记录
      await fetchUserData();
      await fetchHistory();

    } catch (err) {
      console.error('Meme generation error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <Head>
        <title>AI 梗图生成器 - AI 创作平台</title>
      </Head>

      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>AI 梗图生成器</h1>
        <p className={styles.creditsDisplay}>
          剩余额度：<strong>{credits !== null ? credits : '加载中...'}</strong>
        </p>
      </div>

      <div className={styles.generatorArea}>
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
            className={styles.select}
            value={selectedSize}
            onChange={(e) => setSelectedSize(e.target.value)}
            disabled={loading || (credits !== null && credits <= 0)}
          >
            <option value="vertical">竖屏 (1024x1920)</option>
            <option value="horizontal">横屏 (1920x1024)</option>
            <option value="square">方形 (1024x1024)</option>
          </select>
          <button type="submit" className={styles.button} disabled={loading || (credits !== null && credits <= 0)}>
            {loading ? '生成中...' : '生成梗图'}
          </button>
        </form>
      </div>

      {loading && <p className={styles.statusText}>AI 正在奋力创作中，请稍候...</p>}
      {error && <p className={styles.errorText}>{error}</p>}

      {imageUrl && (
        <div className={styles.resultSection}>
          <h2 className={styles.sectionTitle}>生成结果</h2>
          <div className={styles.imageWrapper}>
             <img src={imageUrl} alt="AI 生成的梗图" className={styles.generatedImage} />
          </div>
          <a href={imageUrl} download={`meme_${new Date().getTime()}.png`} className={styles.downloadButton}>
            下载梗图
          </a>
        </div>
      )}

      <div className={styles.historySection}>
        <h2 className={styles.sectionTitle}>你的历史梗图</h2>
        {history.length > 0 ? (
          <div className={styles.historyGrid}>
            {history.map((item) => (
              <div key={item.id} className={styles.historyItem}>
                <img
                  src={`${process.env.NEXT_PUBLIC_API_BASE_URL}${item.image_url}`}
                  alt={item.riddle_answer}
                  className={styles.historyImage}
                />
                <p className={styles.historyCaption}>{item.riddle_answer}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className={styles.noHistoryText}>暂无历史记录，快来生成你的第一张梗图吧！</p>
        )}
      </div>
    </div>
  );
}