import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Descriptions, Form, Input, Row, Space, Table, Tag, Typography, message } from 'antd';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

export default function IdentityProviderPage() {
  const [readiness, setReadiness] = useState(null);
  const [status, setStatus] = useState(null);
  const [ldapResult, setLdapResult] = useState(null);
  const [mappingResult, setMappingResult] = useState(null);
  const [ssoResult, setSsoResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [r, s] = await Promise.all([api.identityProductionReadiness(), api.identityProviderStatus()]);
      setReadiness(r); setStatus(s);
    } catch (e) { message.error(e.message); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const runLdapTest = async () => {
    try { setLdapResult(await api.ldapTestConnection({})); message.success('LDAP test completed'); }
    catch (e) { message.error(e.message); }
  };
  const previewMapping = async (values) => {
    try { setMappingResult(await api.ldapPreviewUser(values)); message.success('Mapping preview completed'); }
    catch (e) { message.error(e.message); }
  };
  const dryRunSso = async (values) => {
    try { setSsoResult(await api.ssoAssertionDryRun(values)); message.success('SSO dry-run completed'); }
    catch (e) { message.error(e.message); }
  };

  return <div>
    <PageHeader title="LDAP/SSO Production" subtitle="Kiểm tra cấu hình định danh tập trung, ánh xạ người dùng và sẵn sàng triển khai production." />
    <Row gutter={[16,16]}>
      <Col xs={24} lg={12}>
        <Card title="Production readiness" loading={loading} extra={<Button onClick={load}>Tải lại</Button>}>
          {readiness && <>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Trạng thái"><Tag color={readiness.status === 'PRODUCTION_READY' ? 'green' : 'orange'}>{readiness.status}</Tag></Descriptions.Item>
              <Descriptions.Item label="Điểm sẵn sàng">{readiness.readiness_score}%</Descriptions.Item>
              <Descriptions.Item label="LDAP">{readiness.ldap_enabled ? 'Enabled' : 'Disabled'} / Dry-run: {String(readiness.ldap_dry_run)}</Descriptions.Item>
              <Descriptions.Item label="SSO">{readiness.sso_enabled ? 'Enabled' : 'Disabled'} - {readiness.sso_provider_name}</Descriptions.Item>
            </Descriptions>
            <Table style={{ marginTop: 16 }} size="small" pagination={false} rowKey="name" dataSource={readiness.checks || []} columns={[
              { title: 'Kiểm tra', dataIndex: 'name' },
              { title: 'Kết quả', dataIndex: 'passed', render: v => <Tag color={v ? 'green' : 'orange'}>{v ? 'OK' : 'Cần cấu hình'}</Tag> },
              { title: 'Ghi chú', dataIndex: 'detail' }
            ]} />
          </>}
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Identity provider status">
          <JsonView data={status || {}} />
          <Button style={{ marginTop: 12 }} type="primary" onClick={runLdapTest}>Test LDAP connection</Button>
          {ldapResult && <JsonView data={ldapResult} />}
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="LDAP user mapping preview">
          <Form layout="vertical" onFinish={previewMapping} initialValues={{ username: 'ldap.test', full_name: 'LDAP Test User', role_code: 'ATTT_OFFICER' }}>
            <Form.Item name="username" label="Username" rules={[{ required: true }]}><Input /></Form.Item>
            <Form.Item name="email" label="Email"><Input /></Form.Item>
            <Form.Item name="full_name" label="Họ tên"><Input /></Form.Item>
            <Form.Item name="role_code" label="Role code"><Input /></Form.Item>
            <Form.Item name="organization_code" label="Organization code"><Input /></Form.Item>
            <Button htmlType="submit" type="primary">Preview mapping</Button>
          </Form>
          {mappingResult && <JsonView data={mappingResult} />}
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="SSO assertion dry-run">
          <Alert type="info" showIcon message="Dry-run không xác thực thật; dùng để kiểm tra mapping claim sang user nội bộ." style={{ marginBottom: 12 }} />
          <Form layout="vertical" onFinish={dryRunSso} initialValues={{ username: 'sso.test', full_name: 'SSO Test User', role_code: 'REVIEWER', provider_name: 'Enterprise SSO' }}>
            <Form.Item name="provider_name" label="Provider"><Input /></Form.Item>
            <Form.Item name="username" label="Username" rules={[{ required: true }]}><Input /></Form.Item>
            <Form.Item name="email" label="Email"><Input /></Form.Item>
            <Form.Item name="full_name" label="Họ tên"><Input /></Form.Item>
            <Form.Item name="role_code" label="Role code"><Input /></Form.Item>
            <Button htmlType="submit" type="primary">Run SSO dry-run</Button>
          </Form>
          {ssoResult && <JsonView data={ssoResult} />}
        </Card>
      </Col>
    </Row>
  </div>;
}
