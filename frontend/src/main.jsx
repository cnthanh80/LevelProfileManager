import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Alert, Spin } from 'antd';
import 'antd/dist/reset.css';
import AppLayout from './components/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import { NotificationsPage, ProfilesPage, SystemsPage } from './pages/ListPages';
import { api, getToken } from './api/client';

function App() {
  const [user, setUser] = useState(null);
  const [active, setActive] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState({});

  const load = async () => {
    setError('');
    setLoading(true);
    try {
      if (!getToken()) { setUser(null); return; }
      const me = await api.me();
      setUser(me);
      const [summary, workflow, compliance, gaps, enterprise, executive, systems, profiles, notifications] = await Promise.all([
        api.dashboardSummary(),
        api.workflowSummary(),
        api.complianceOverview(),
        api.evidenceGaps(),
        api.enterpriseOverview(),
        api.enterpriseReport(),
        api.systems(),
        api.profiles(),
        api.notifications()
      ]);
      setData({
        summary, workflow, compliance, gaps, enterprise, executive,
        systems: systems.items || [], profiles: profiles.items || [], notifications: notifications.items || notifications || []
      });
    } catch (e) {
      setError(e.message || 'Không tải được dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (!getToken() || !user) return <LoginPage onLogin={load} />;

  let page = <DashboardPage data={data} />;
  if (active === 'systems') page = <SystemsPage items={data.systems} />;
  if (active === 'profiles') page = <ProfilesPage items={data.profiles} />;
  if (active === 'notifications') page = <NotificationsPage items={data.notifications} />;

  return (
    <AppLayout active={active} setActive={setActive} user={user}>
      {loading ? <Spin /> : error ? <Alert type="error" message="Lỗi" description={error} /> : page}
    </AppLayout>
  );
}

createRoot(document.getElementById('root')).render(<App />);
