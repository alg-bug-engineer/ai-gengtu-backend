// alg-bug-engineer/ai-gengtu-backend/ai-gengtu-backend-683d3a06f02d6e71016f8d8e977d1795d9f89ed9/ai-gengtu-frontend/pages/_app.js
import Layout from '../components/Layout';
import "@/styles/globals.css";

function MyApp({ Component, pageProps }) {
  // 登录和注册页面不使用 Layout 组件
  const noLayout = Component.name === 'LoginPage' || Component.name === 'RegisterPage';

  if (noLayout) {
    return <Component {...pageProps} />;
  }

  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}

export default MyApp;