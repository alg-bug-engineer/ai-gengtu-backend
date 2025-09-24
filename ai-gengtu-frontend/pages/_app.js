import Layout from '../components/Layout';
import "@/styles/globals.css";

export default function App({ Component, pageProps }) {
  // 登录和注册页面不使用 Layout 组件
  const isLoginPage = Component.name === 'LoginPage' || Component.name === 'RegisterPage';
  
  if (isLoginPage) {
    return <Component {...pageProps} />;
  }

  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}