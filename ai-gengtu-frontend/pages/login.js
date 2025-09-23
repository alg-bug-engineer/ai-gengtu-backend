// pages/login.js
import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('handleSubmit: Login form submitted.');
    console.log('Attempting to log in with email:', email);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5550/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include', 
      });

      console.log('API call to /api/login finished with status:', response.status);

      const data = await response.json();
      if (!response.ok) {
        console.error('Login failed. API message:', data.message);
        throw new Error(data.message || 'Login failed');
      }

      console.log('Login successful. Redirecting to home page.');
      router.push('/');
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message);
    } finally {
      console.log('handleSubmit: Function finished. Setting loading to false.');
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '400px', margin: 'auto', textAlign: 'center' }}>
      <Head><title>登录 - AI 梗图生成器</title></Head>
      <h1>登录</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <input
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            console.log('Email input changed:', e.target.value);
          }}
          placeholder="邮箱"
          disabled={loading}
          style={{ padding: '0.5rem', fontSize: '1rem' }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            console.log('Password input changed.');
          }}
          placeholder="密码"
          disabled={loading}
          style={{ padding: '0.5rem', fontSize: '1rem' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '0.5rem', fontSize: '1rem' }}>
          {loading ? '登录中...' : '登录'}
        </button>
      </form>
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}
      <p style={{ marginTop: '1rem' }}>
        还没有账户？<Link href="/register">注册</Link>
      </p>
    </div>
  );
}