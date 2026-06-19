import { Button, Card, Form, Input, Typography, Alert } from 'antd';
import { useState } from 'react';
import { login } from '../api/client';

export default function LoginPage({ onLogin }) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (values) => {
    setError('');
    setLoading(true);
    try {
      await login(values.username, values.password);
      onLogin();
    } catch (e) {
      setError('Đăng nhập không thành công. Kiểm tra username/password hoặc backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5' }}>
      <Card style={{ width: 420 }}>
        <Typography.Title level={3}>Level Profile Manager</Typography.Title>
        <Typography.Paragraph>Đăng nhập hệ thống quản lý hồ sơ đề xuất cấp độ.</Typography.Paragraph>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        <Form layout="vertical" initialValues={{ username: 'admin', password: 'Admin@123' }} onFinish={submit}>
          <Form.Item label="Username" name="username" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label="Password" name="password" rules={[{ required: true }]}><Input.Password /></Form.Item>
          <Button block type="primary" htmlType="submit" loading={loading}>Đăng nhập</Button>
        </Form>
      </Card>
    </div>
  );
}
