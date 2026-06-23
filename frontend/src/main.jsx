import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Alert, Button, ConfigProvider, Spin, theme } from 'antd';
import 'antd/dist/reset.css';
import AppLayout from './components/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import OrganizationsPage from './pages/OrganizationsPage';
import SystemsPage from './pages/SystemsPage';
import ProfilesPage from './pages/ProfilesPage';
import CompliancePage from './pages/CompliancePage';
import DocumentsPage from './pages/DocumentsPage';
import GovernmentDossierPage from './pages/GovernmentDossierPage';
import TemplateCenterPage from './pages/TemplateCenterPage';
import DigitalDossierPage from './pages/DigitalDossierPage';
import NotificationsPage from './pages/NotificationsPage';
import ReviewsPage from './pages/ReviewsPage';
import AuditPage from './pages/AuditPage';
import AdminPage from './pages/AdminPage';
import ReleasePage from './pages/ReleasePage';
import RiskSlaPage from './pages/RiskSlaPage';
import AssessmentPortalPage from './pages/AssessmentPortalPage';
import AssessmentWorkflowPage from './pages/AssessmentWorkflowPage';
import ExecutiveDashboardPage from './pages/ExecutiveDashboardPage';
import AiClassificationPage from './pages/AiClassificationPage';
import RealSignaturePage from './pages/RealSignaturePage';
import CmdbPage from './pages/CmdbPage';
import IdentityProviderPage from './pages/IdentityProviderPage';
import SiemIntegrationPage from './pages/SiemIntegrationPage';
import ComplianceAutomationPage from './pages/ComplianceAutomationPage';
import ComplianceMonitoringPage from './pages/ComplianceMonitoringPage';
import EnterpriseReportingPage from './pages/EnterpriseReportingPage';
import EnterpriseCenterPage from './pages/EnterpriseCenterPage';
import { api, clearToken, getToken } from './api/client';

function pickItems(x) { return Array.isArray(x?.items) ? x.items : Array.isArray(x) ? x : []; }

function App() {
  const [user, setUser] = useState(null);
  const [active, setActive] = useState(localStorage.getItem('lpm_active_menu') || 'dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState({});

  const load = async () => {
    setError(''); setLoading(true);
    try {
      if (!getToken()) { setUser(null); setLoading(false); return; }
      const me = await api.me(); setUser(me);
      const calls = await Promise.allSettled([
        api.dashboardSummary(), api.workflowSummary(), api.complianceOverview(), api.evidenceGaps(), api.enterpriseOverview(), api.enterpriseReport(), api.enterpriseLevelMatrix(), api.enterpriseActionBoard(), api.complianceDashboard(), api.periodicReviewDashboard(),
        api.systems({ limit: 200 }), api.profiles({ limit: 200 }), api.notifications({ limit: 20 })
      ]);
      const val = (i, fallback) => calls[i].status === 'fulfilled' ? calls[i].value : fallback;
      setData({
        summary: val(0, {}), workflow: val(1, {}), compliance: val(2, {}), gaps: val(3, []), enterprise: val(4, {}), executive: val(5, {}), levelMatrix: val(6, []), actionBoard: val(7, []), complianceDashboard: val(8, {}), reviewDashboard: val(9, {}),
        systems: pickItems(val(10, [])), profiles: pickItems(val(11, [])), notifications: pickItems(val(12, []))
      });
    } catch (e) {
      setError(e.message || 'Không tải được dữ liệu');
      if (String(e.message || '').includes('401')) clearToken();
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => { localStorage.setItem('lpm_active_menu', active); }, [active]);

  if (!getToken() || !user) return <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}><LoginPage onLogin={load} /></ConfigProvider>;

  let page = <DashboardPage data={data} />;
  if (active === 'organizations') page = <OrganizationsPage />;
  if (active === 'systems') page = <SystemsPage items={data.systems} reload={load} />;
  if (active === 'profiles') page = <ProfilesPage items={data.profiles} systems={data.systems} reload={load} />;
  if (active === 'compliance') page = <CompliancePage profiles={data.profiles} />;
  if (active === 'ai-classification') page = <AiClassificationPage profiles={data.profiles} />;
  if (active === 'documents') page = <DocumentsPage profiles={data.profiles} />;
  if (active === 'government-dossier') page = <GovernmentDossierPage profiles={data.profiles} />;
  if (active === 'templates') page = <TemplateCenterPage profiles={data.profiles} />;
  if (active === 'dossier') page = <DigitalDossierPage profiles={data.profiles} />;
  if (active === 'real-signature') page = <RealSignaturePage profiles={data.profiles} />;
  if (active === 'reviews') page = <ReviewsPage />;
  if (active === 'risk-sla') page = <RiskSlaPage profiles={data.profiles} systems={data.systems} />;
  if (active === 'assessment') page = <AssessmentPortalPage profiles={data.profiles} />;
  if (active === 'assessment-workflow') page = <AssessmentWorkflowPage />;
  if (active === 'cmdb') page = <CmdbPage profiles={data.profiles} systems={data.systems} />;
  if (active === 'executive') page = <ExecutiveDashboardPage />;
  if (active === 'notifications') page = <NotificationsPage />;
  if (active === 'audit') page = <AuditPage />;
  if (active === 'admin') page = <AdminPage />;
  if (active === 'identity-provider') page = <IdentityProviderPage />;
  if (active === 'siem') page = <SiemIntegrationPage />;
  if (active === 'compliance-automation') page = <ComplianceAutomationPage profiles={data.profiles} />;
  if (active === 'compliance-monitoring') page = <ComplianceMonitoringPage profiles={data.profiles} />;
  if (active === 'enterprise-reporting') page = <EnterpriseReportingPage />;
  if (active === 'enterprise-center') page = <EnterpriseCenterPage />;
  if (active === 'release') page = <ReleasePage />;

  return <ConfigProvider theme={{ token: { borderRadius: 8 } }}>
    <AppLayout active={active} setActive={setActive} user={user}>
      {loading ? <div style={{ padding: 80, textAlign: 'center' }}><Spin size="large" /></div> : error ? <Alert type="error" showIcon message="Lỗi" description={error} action={<Button onClick={load}>Tải lại</Button>} /> : page}
    </AppLayout>
  </ConfigProvider>;
}

createRoot(document.getElementById('root')).render(<App />);
