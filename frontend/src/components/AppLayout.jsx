import { Layout, Menu, Typography, Button, Space } from 'antd';
import { DashboardOutlined, DatabaseOutlined, FileProtectOutlined, BellOutlined, LogoutOutlined } from '@ant-design/icons';
import { clearToken } from '../api/client';

const { Header, Sider, Content } = Layout;

export default function AppLayout({ active, setActive, children, user }) {
  const items = [
    { key: 'dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: 'systems', icon: <DatabaseOutlined />, label: 'Hệ thống thông tin' },
    { key: 'profiles', icon: <FileProtectOutlined />, label: 'Hồ sơ cấp độ' },
    { key: 'notifications', icon: <BellOutlined />, label: 'Thông báo' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={260} theme="dark">
        <div style={{ color: '#fff', padding: 20, fontWeight: 700, fontSize: 18 }}>
          Level Profile Manager
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[active]} items={items} onClick={({ key }) => setActive(key)} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 24px' }}>
          <Typography.Title level={4} style={{ margin: 0 }}>Quản lý hồ sơ đề xuất cấp độ ATHTTT</Typography.Title>
          <Space>
            <span>{user?.full_name || user?.username}</span>
            <Button icon={<LogoutOutlined />} onClick={() => { clearToken(); location.reload(); }}>Đăng xuất</Button>
          </Space>
        </Header>
        <Content style={{ margin: 24 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
