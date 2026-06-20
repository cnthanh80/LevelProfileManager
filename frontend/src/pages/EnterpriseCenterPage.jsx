import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Progress, Row, Space, Statistic, Table, Tag, Typography } from 'antd';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

function tagColor(status) {
  if (status === 'UP' || status === 'PASS' || status === 'ENTERPRISE_READY') return 'green';
  if (status === 'DOWN' || status === 'FAIL' || status === 'NEEDS_ATTENTION') return 'red';
  return 'orange';
}

export default function EnterpriseCenterPage() {
  const [data, setData] = useState(null);
  const [configs, setConfigs] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      await api.enterpriseSeedDefaults();
      const [dashboard, cfg, job, pol, bkp] = await Promise.all([
        api.enterpriseCenterDashboard(),
        api.enterpriseConfigurations({ limit: 100 }),
        api.enterpriseJobs({ limit: 100 }),
        api.enterpriseRetentionPolicies({ limit: 100 }),
        api.enterpriseBackups({ limit: 20 }),
      ]);
      setData(dashboard);
      setConfigs(cfg.items || []);
      setJobs(job.items || []);
      setPolicies(pol.items || []);
      setBackups(bkp.items || []);
    } catch (e) { setError(e.message || 'Không tải được dữ liệu Enterprise Center'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const runHealth = async () => { await api.enterpriseHealth(); await load(); };
  const mockBackup = async () => { await api.enterpriseCreateMockBackup({ backup_type: 'LOGICAL', scope: 'DATABASE', status: 'COMPLETED', size_mb: 128, notes: 'Frontend v4.0 mock backup' }); await load(); };

  const readiness = data?.readiness || {};
  const health = data?.health || {};

  return <Space direction="vertical" size="middle" style={{ width: '100%' }}>
    <PageHeader title="Enterprise Center v4.0" subtitle="Trung tâm cấu hình, sức khỏe, scheduler, retention, backup và enterprise readiness" />
    {error && <Alert type="error" showIcon message={error} />}
    <Space wrap>
      <Button type="primary" loading={loading} onClick={load}>Tải lại</Button>
      <Button onClick={runHealth}>Chạy Health Check</Button>
      <Button onClick={mockBackup}>Tạo mock backup</Button>
    </Space>

    <Row gutter={[16,16]}>
      <Col xs={24} md={6}><Card><Statistic title="Readiness" value={readiness.overall_score || 0} suffix="/100" /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Health" value={health.status || 'UNKNOWN'} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Config" value={data?.configuration_count || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Job bật" value={data?.enabled_job_count || 0} /></Card></Col>
    </Row>

    <Card title="Enterprise Readiness">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space><Tag color={tagColor(readiness.readiness_level)}>{readiness.readiness_level || 'UNKNOWN'}</Tag><Progress percent={readiness.overall_score || 0} style={{ width: 300 }} /></Space>
        <Table rowKey="domain" dataSource={readiness.checks || []} pagination={false} columns={[
          { title: 'Miền kiểm tra', dataIndex: 'domain' },
          { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={tagColor(v)}>{v}</Tag> },
          { title: 'Điểm', dataIndex: 'score' },
          { title: 'Ghi chú', dataIndex: 'message' },
        ]} />
        {(readiness.recommendations || []).map((x, i) => <Alert key={i} type="info" showIcon message={x} />)}
      </Space>
    </Card>

    <Card title="System Health Center">
      <Table rowKey="id" dataSource={health.components || []} pagination={false} columns={[
        { title: 'Mã', dataIndex: 'component_code' },
        { title: 'Thành phần', dataIndex: 'component_name' },
        { title: 'Nhóm', dataIndex: 'component_group' },
        { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={tagColor(v)}>{v}</Tag> },
        { title: 'Latency', dataIndex: 'latency_ms', render: v => v == null ? '-' : `${v} ms` },
        { title: 'Thông điệp', dataIndex: 'message' },
      ]} />
    </Card>

    <Card title="Enterprise Configuration Center">
      <Table rowKey="id" dataSource={configs} pagination={{ pageSize: 8 }} columns={[
        { title: 'Nhóm', dataIndex: 'config_group' },
        { title: 'Key', dataIndex: 'config_key' },
        { title: 'Tên', dataIndex: 'display_name' },
        { title: 'Giá trị', render: (_, r) => r.is_secret ? '********' : (r.config_value || '-') },
        { title: 'Bật', dataIndex: 'is_enabled', render: v => <Tag color={v ? 'green' : 'default'}>{String(v)}</Tag> },
      ]} />
    </Card>

    <Card title="Job Scheduler Center">
      <Table rowKey="id" dataSource={jobs} pagination={{ pageSize: 8 }} columns={[
        { title: 'Nhóm', dataIndex: 'job_group' },
        { title: 'Job', dataIndex: 'job_code' },
        { title: 'Tên', dataIndex: 'job_name' },
        { title: 'Lịch', dataIndex: 'schedule_expression' },
        { title: 'Bật', dataIndex: 'is_enabled', render: v => <Tag color={v ? 'green' : 'default'}>{String(v)}</Tag> },
        { title: 'Trạng thái', dataIndex: 'last_status' },
      ]} />
    </Card>

    <Card title="Data Retention Policy">
      <Table rowKey="id" dataSource={policies} pagination={{ pageSize: 8 }} columns={[
        { title: 'Policy', dataIndex: 'policy_code' },
        { title: 'Dữ liệu', dataIndex: 'data_domain' },
        { title: 'Ngày lưu', dataIndex: 'retention_days' },
        { title: 'Archive', dataIndex: 'archive_enabled', render: v => String(v) },
        { title: 'Purge', dataIndex: 'purge_enabled', render: v => String(v) },
        { title: 'Legal hold', dataIndex: 'legal_hold', render: v => String(v) },
      ]} />
    </Card>

    <Card title="Backup & Recovery Center">
      <Table rowKey="id" dataSource={backups} pagination={{ pageSize: 8 }} columns={[
        { title: 'Backup code', dataIndex: 'backup_code' },
        { title: 'Loại', dataIndex: 'backup_type' },
        { title: 'Scope', dataIndex: 'scope' },
        { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={v === 'COMPLETED' ? 'green' : 'orange'}>{v}</Tag> },
        { title: 'Size MB', dataIndex: 'size_mb' },
        { title: 'Validation', dataIndex: 'validation_status' },
      ]} />
    </Card>

    <Card title="Raw dashboard JSON"><JsonView data={data || {}} /></Card>
    <Typography.Text type="secondary">LevelProfileManager Enterprise Release v4.0</Typography.Text>
  </Space>;
}
