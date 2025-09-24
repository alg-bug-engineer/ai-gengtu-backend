// alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/ai-gengtu-frontend/pages/figurine_generator.js
import { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function FigurineGeneratorPage() {
  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [credits, setCredits] = useState(null);
  const [history, setHistory] = useState([]);

  const fetchUserData = useCallback(async () => {
    try {
      const userRes = await fetch('http://8.149.232.39:5550/api/user', { credentials: 'include' });
      if (userRes.ok) {
        const userData = await userRes.json();
        setCredits(userData.credits);
      } else {
        window.location.href = '/login';
      }
    } catch (err) {
      console.error('Failed to fetch user data:', err);
      setError('无法加载用户信息，请检查网络连接。');
    }
  }, []);

  // 注意：这里我们让历史记录获取所有类型的生成，也可以后续在后端增加type字段进行区分
  const fetchHistory = useCallback(async () => {
    try {
      const historyRes = await fetch('http://8.149.232.39:5550/api/history', { credentials: 'include' });
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        // 简单过滤一下，只显示手办历史
        setHistory(historyData.filter(item => item.riddle_answer === "立体雕塑作品"));
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
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setImageFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    } else {
      setImageFile(null);
      setPreviewUrl(null);
      setError("请选择一个有效的图片文件。");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageFile) {
      setError('请先上传一张图片。');
      return;
    }
    setLoading(true);
    setError(null);
    setImageUrl(null);

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await fetch('http://8.149.232.39:5550/api/generate_figurine', {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `生成失败 (状态码: ${response.status})`);
      }

      const imageBlob = await response.blob();
      const objectURL = URL.createObjectURL(imageBlob);
      setImageUrl(objectURL);

      await fetchUserData();
      await fetchHistory();

    } catch (err) {
      console.error('Figurine generation error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <Head>
        <title>立体雕塑 - AI 创作平台</title>
      </Head>

      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>立体雕塑</h1>
        <p className={styles.creditsDisplay}>
          剩余额度：<strong>{credits !== null ? credits : '加载中...'}</strong>
        </p>
      </div>

      <div className={styles.generatorArea}>
        <p className={styles.uploadDescription}>
          请上传一张包含人物、最好是正面的照片，AI 将为您创造一款独特的立体手办艺术图。
        </p>
        <form onSubmit={handleSubmit} className={styles.uploadForm}>
          <input
            type="file"
            id="imageUpload"
            className={styles.fileInput}
            onChange={handleFileChange}
            accept="image/png, image/jpeg, image/webp"
            disabled={loading || (credits !== null && credits <= 0)}
          />
          <label htmlFor="imageUpload" className={styles.uploadLabel}>
            {previewUrl ? '更换图片' : '上传图片'}
          </label>
          
          {previewUrl && <img src={previewUrl} alt="Preview" className={styles.imagePreview} />}

          <button type="submit" className={styles.button} disabled={!imageFile || loading || (credits !== null && credits <= 0)}>
            {loading ? '生成中...' : '生成手办'}
          </button>
        </form>
      </div>
      
      {loading && <p className={styles.statusText}>AI 正在进行艺术加工，请稍候...</p>}
      {error && <p className={styles.errorText}>{error}</p>}

      {imageUrl && (
        <div className={styles.resultSection}>
          <h2 className={styles.sectionTitle}>生成结果</h2>
          <div className={styles.imageWrapper}>
             <img src={imageUrl} alt="AI 生成的手办图" className={styles.generatedImage} />
          </div>
          <a href={imageUrl} download={`figurine_${new Date().getTime()}.png`} className={styles.downloadButton}>
            下载图片
          </a>
        </div>
      )}

      <div className={styles.historySection}>
        <h2 className={styles.sectionTitle}>历史作品</h2>
        {history.length > 0 ? (
          <div className={styles.historyGrid}>
            {history.map((item) => (
              <div key={item.id} className={styles.historyItem}>
                <img
                  src={`http://8.149.232.39:5550${item.image_url}`}
                  alt={item.riddle_answer}
                  className={styles.historyImage}
                />
              </div>
            ))}
          </div>
        ) : (
           <p className={styles.noHistoryText}>暂无历史作品，快来创造你的第一个数字手办吧！</p>
        )}
      </div>
    </div>
  );
}