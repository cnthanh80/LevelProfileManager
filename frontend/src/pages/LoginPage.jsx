import { Alert, Button, Card, Divider, Form, Input, Space, Typography } from 'antd';
import { SafetyCertificateOutlined } from '@ant-design/icons';
import React, { useState } from 'react';
import { login, api } from '../api/client';

export default function LoginPage({ onLogin }) {
  const [error, setError] = useState('');
  const [hint, setHint] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (values) => {
    setError(''); setLoading(true);
    try { await login(values.username, values.password); await onLogin(); }
    catch (e) { setError(e.message || 'Đăng nhập không thành công.'); }
    finally { setLoading(false); }
  };

  const loadSsoHint = async () => {
    try { setHint(await api.ssoLoginHint()); } catch (e) { setHint({ message: 'SSO chưa cấu hình hoặc backend không trả về gợi ý.' }); }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', background: 'linear-gradient(135deg,#0b1f3a,#153b68)' }}>
      <div style={{ color: '#fff', padding: 72, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <SafetyCertificateOutlined style={{ fontSize: 56, marginBottom: 24 }} />
        <Typography.Title style={{ color: '#fff', marginBottom: 12 }}>Level Profile Manager</Typography.Title>
        <Typography.Title level={3} style={{ color: '#d6e4ff', fontWeight: 400 }}>Quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin</Typography.Title>
        <Typography.Paragraph style={{ color: '#c9d6e8', fontSize: 16, maxWidth: 680 }}>
          Hỗ trợ khai báo hệ thống, hồ sơ cấp độ, checklist ATTT, minh chứng, workflow phê duyệt, xuất biểu mẫu và giám sát rà soát định kỳ.
        </Typography.Paragraph>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 32 }}>
        <Card style={{ width: 430, boxShadow: '0 20px 60px rgba(0,0,0,.25)' }}>
          <Typography.Title level={3}>Đăng nhập</Typography.Title>
          <Typography.Text type="secondary">Tài khoản seed mặc định: admin / Admin@123</Typography.Text>
          <Divider />
          {error && <Alert type="error" showIcon message="Không đăng nhập được" description={error} style={{ marginBottom: 16 }} />}
          {hint && <Alert type="info" showIcon message="SSO/LDAP" description={hint.message || JSON.stringify(hint)} style={{ marginBottom: 16 }} />}
          <Form layout="vertical" initialValues={{ username: 'admin', password: 'Admin@123' }} onFinish={submit}>
            <Form.Item label="Username" name="username" rules={[{ required: true, message: 'Nhập username' }]}><Input autoFocus /></Form.Item>
            <Form.Item label="Password" name="password" rules={[{ required: true, message: 'Nhập password' }]}><Input.Password /></Form.Item>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button block type="primary" htmlType="submit" loading={loading}>Đăng nhập</Button>
              <Button block onClick={loadSsoHint}>Kiểm tra SSO/LDAP Hint</Button>
            </Space>
          </Form>
        </Card>
      </div>
    </div>
  );
}
