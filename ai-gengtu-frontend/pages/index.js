import { useState } from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css'; // 引入样式文件

export default function HomePage() {
  const [answer, setAnswer] = useState('');
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // 阻止表单提交时，浏览器默认刷新行为
    
    // 状态初始化，开始请求
    setLoading(true);
    setError(null);
    setImageUrl(null);

    // 验证用户输入
    if (!answer) {
      setError('请输入一个谜底词语。');
      setLoading(false);
      return;
    }

    try {
      // 向您的 Flask API 发送请求
      // 请确保您的 Flask 服务正在运行，并且 URL 正确。
      // 在本地开发中，通常是 http://localhost:5000。
      const response = await fetch('http://localhost:5550/generate_meme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer }),
      });

      // 检查响应状态
      if (!response.ok) {
        // 如果 API 响应状态码不是 2xx，抛出错误
        const errorData = await response.json();
        throw new Error(errorData.message || 'API 请求失败，请检查后端服务。');
      }

      // 获取响应的 Blob 数据
      const imageBlob = await response.blob();
      // 将 Blob 数据转换成一个本地 URL
      const objectURL = URL.createObjectURL(imageBlob);
      setImageUrl(objectURL);

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>AI 梗图生成器</title>
        <meta name="description" content="用 AI 创作有趣的梗图" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>AI 梗图生成器</h1>
        <p className={styles.description}>输入一个词语作为梗图谜底，让 AI 创作！</p>

        <form className={styles.form} onSubmit={handleSubmit}>
          <input
            type="text"
            className={styles.input}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="例如：东施效颦"
            disabled={loading}
          />
          <button type="submit" className={styles.button} disabled={loading}>
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