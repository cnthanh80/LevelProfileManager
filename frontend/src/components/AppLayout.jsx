import { Layout, Menu, Typography, Button, Space, Avatar, Tag } from 'antd';
import { AuditOutlined, BarChartOutlined, BellOutlined, DatabaseOutlined, FileDoneOutlined, FileProtectOutlined, FileTextOutlined, LogoutOutlined, SafetyCertificateOutlined, SettingOutlined, SolutionOutlined, SyncOutlined } from '@ant-design/icons';
import { clearToken } from '../api/client';

const { Header, Sider, Content } = Layout;

export default function AppLayout({ active, setActive, children, user }) {
  const items = [
    { key: 'dashboard', icon: <BarChartOutlined />, label: 'Dashboard' },
    { key: 'systems', icon: <DatabaseOutlined />, label: 'Hệ thống thông tin' },
    { key: 'profiles', icon: <FileProtectOutlined />, label: 'Hồ sơ cấp độ' },
    { key: 'compliance', icon: <SafetyCertificateOutlined />, label: 'Compliance Engine' },
    { key: 'documents', icon: <FileTextOutlined />, label: 'Tài liệu/Xuất hồ sơ' },
    { key: 'reviews', icon: <SyncOutlined />, label: 'Rà soát định kỳ' },
    { key: 'notifications', icon: <BellOutlined />, label: 'Thông báo' },
    { key: 'audit', icon: <AuditOutlined />, label: 'Audit Trail' },
    { key: 'admin', icon: <SettingOutlined />, label: 'Quản trị' },
    { key: 'release', icon: <FileDoneOutlined />, label: 'Release/UAT' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={290} theme="dark" breakpoint="lg" collapsedWidth="0">
        <div style={{ color: '#fff', padding: 20 }}>
          <Space align="center">
            <Avatar icon={<SolutionOutlined />} />
            <div>
              <div style={{ fontWeight: 800, fontSize: 17 }}>LevelProfileManager</div>
              <div style={{ color: '#adc6ff', fontSize: 12 }}>ATHTTT theo cấp độ</div>
            </div>
          </Space>
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[active]} items={items} onClick={({ key }) => setActive(key)} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 24px', boxShadow: '0 1px 6px rgba(0,0,0,.08)' }}>
          <div>
            <Typography.Title level={4} style={{ margin: 0 }}>Quản lý hồ sơ đề xuất cấp độ ATHTTT</Typography.Title>
            <Typography.Text type="secondary">MVP 2.1 · Frontend Business UI Complete</Typography.Text>
          </div>
          <Space>
            <Tag color="blue">{user?.role?.name || user?.role_name || 'USER'}</Tag>
            <span>{user?.full_name || user?.username}</span>
            <Button icon={<LogoutOutlined />} onClick={() => { clearToken(); location.reload(); }}>Đăng xuất</Button>
          </Space>
        </Header>
        <Content style={{ margin: 24 }}>{children}</Content>
      </Layout>
    </Layout>
  );
}
