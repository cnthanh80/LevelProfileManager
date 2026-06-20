import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, Row, Select, Space, Statistic, Table, Tag, Typography } from 'antd';
import { api } from '../api/client';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';

const severityColor = { INFO: 'blue', LOW: 'cyan', MEDIUM: 'gold', HIGH: 'orange', CRITICAL: 'red' };

export default function SiemIntegrationPage() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [connectors, setConnectors] = useState([]);
  const [events, setEvents] = useState([]);
  const [rules, setRules] = useState([]);
  const [correlation, setCorrelation] = useState({});
  const [message, setMessage] = useState('');
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true); setMessage('');
    try {
      const [st, db, con, ev, ru, co] = await Promise.all([
        api.siemStatus(), api.siemDashboard(), api.siemConnectors({ limit: 50 }), api.siemEvents({ limit: 50 }), api.siemRules({ limit: 50 }), api.siemCorrelationSummary()
      ]);
      setStatus(st); setDashboard(db); setConnectors(con.items || []); setEvents(ev.items || []); setRules(ru.items || []); setCorrelation(co);
    } catch (e) {
      setMessage(e.message || 'Không tải được dữ liệu SIEM');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const seed = async () => {
    setLoading(true);
    try {
      await api.seedSiemConnectors();
      await api.seedSiemRules();
      await load();
    } finally { setLoading(false); }
  };

  const ingest = async (values) => {
    setLoading(true);
    try {
      await api.ingestSiemEvent(values);
      form.resetFields();
      await load();
    } finally { setLoading(false); }
  };

  const ingestAudit = async () => {
    setLoading(true);
    try { await api.ingestAuditToSiem(); await load(); } finally { setLoading(false); }
  };

  const ingestSecurity = async () => {
    setLoading(true);
    try { await api.ingestSecurityToSiem(); await load(); } finally { setLoading(false); }
  };

  return <div>
    <PageHeader title="SIEM & Audit Integration" subtitle="Tích hợp sự kiện ATTT, audit trail và SOC/SIEM" />
    {message && <Alert type="error" showIcon message={message} style={{ marginBottom: 16 }} />}

    <Row gutter={[16, 16]}>
      <Col xs={24} md={6}><Card><Statistic title="Connector" value={dashboard.total_connectors || 0} suffix={`/ ${dashboard.enabled_connectors || 0} enabled`} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="SIEM Events" value={dashboard.total_events || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Open Events" value={dashboard.open_events || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Risk Score" value={dashboard.risk_score || 0} suffix="/100" /></Card></Col>
    </Row>

    <Card style={{ marginTop: 16 }}>
      <Space wrap>
        <Button type="primary" loading={loading} onClick={seed}>Seed Connector/Rules</Button>
        <Button loading={loading} onClick={ingestAudit}>Import từ Audit Logs</Button>
        <Button loading={loading} onClick={ingestSecurity}>Import từ Security Events</Button>
        <Button onClick={load}>Tải lại</Button>
      </Space>
      <Typography.Paragraph style={{ marginTop: 12 }}>
        Trạng thái: <Tag color="green">{status.status || 'READY'}</Tag> · Supported: {(status.supported_integrations || []).join(', ')}
      </Typography.Paragraph>
    </Card>

    <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
      <Col xs={24} lg={12}>
        <Card title="Ingest sự kiện thử nghiệm">
          <Form form={form} layout="vertical" onFinish={ingest} initialValues={{ event_type: 'AUTH_FAILURE', severity: 'HIGH', source_system: 'LevelProfileManager', status: 'OPEN' }}>
            <Row gutter={12}>
              <Col span={12}><Form.Item label="Event type" name="event_type" rules={[{ required: true }]}><Input /></Form.Item></Col>
              <Col span={12}><Form.Item label="Severity" name="severity"><Select options={['INFO','LOW','MEDIUM','HIGH','CRITICAL'].map(x => ({ value: x, label: x }))} /></Form.Item></Col>
              <Col span={12}><Form.Item label="Username" name="username"><Input /></Form.Item></Col>
              <Col span={12}><Form.Item label="IP" name="ip_address"><Input /></Form.Item></Col>
              <Col span={12}><Form.Item label="Asset code" name="asset_code"><Input /></Form.Item></Col>
              <Col span={12}><Form.Item label="Source" name="source_system"><Input /></Form.Item></Col>
              <Col span={24}><Form.Item label="Raw message" name="raw_message"><Input.TextArea rows={3} /></Form.Item></Col>
            </Row>
            <Button type="primary" htmlType="submit" loading={loading}>Ghi nhận sự kiện</Button>
          </Form>
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Khuyến nghị SOC/SIEM">
          <JsonView data={{ recommendations: dashboard.recommendations || [], correlation }} />
        </Card>
      </Col>
    </Row>

    <Card title="Connectors" style={{ marginTop: 16 }}>
      <Table rowKey="id" loading={loading} dataSource={connectors} pagination={{ pageSize: 5 }} columns={[
        { title: 'Code', dataIndex: 'connector_code' },
        { title: 'Name', dataIndex: 'connector_name' },
        { title: 'Type', dataIndex: 'connector_type', render: v => <Tag>{v}</Tag> },
        { title: 'Enabled', dataIndex: 'is_enabled', render: v => <Tag color={v ? 'green' : 'default'}>{String(v)}</Tag> },
      ]} />
    </Card>

    <Card title="SIEM Events" style={{ marginTop: 16 }}>
      <Table rowKey="id" loading={loading} dataSource={events} pagination={{ pageSize: 8 }} columns={[
        { title: 'ID', dataIndex: 'id', width: 70 },
        { title: 'Type', dataIndex: 'event_type' },
        { title: 'Severity', dataIndex: 'severity', render: v => <Tag color={severityColor[v] || 'default'}>{v}</Tag> },
        { title: 'Status', dataIndex: 'status' },
        { title: 'User', dataIndex: 'username' },
        { title: 'IP', dataIndex: 'ip_address' },
        { title: 'Message', dataIndex: 'normalized_message' },
      ]} />
    </Card>

    <Card title="Correlation Rules" style={{ marginTop: 16 }}>
      <Table rowKey="id" loading={loading} dataSource={rules} pagination={{ pageSize: 5 }} columns={[
        { title: 'Rule', dataIndex: 'rule_code' },
        { title: 'Name', dataIndex: 'rule_name' },
        { title: 'Event', dataIndex: 'event_type' },
        { title: 'Severity', dataIndex: 'min_severity' },
        { title: 'Risk', dataIndex: 'risk_score' },
      ]} />
    </Card>
  </div>;
}
