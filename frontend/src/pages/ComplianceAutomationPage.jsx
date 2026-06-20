import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Row, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { RobotOutlined, ThunderboltOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import { api } from '../api/client';

function sevColor(severity) {
  if (severity === 'CRITICAL') return 'red';
  if (severity === 'HIGH') return 'volcano';
  if (severity === 'MEDIUM') return 'orange';
  return 'blue';
}

export default function ComplianceAutomationPage({ profiles = [] }) {
  const [dashboard, setDashboard] = useState(null);
  const [findings, setFindings] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [d, f, r] = await Promise.all([
        api.complianceAutomationDashboard(),
        api.complianceAutomationFindings({ limit: 50 }),
        api.complianceAutomationRuns({ limit: 10 }),
      ]);
      setDashboard(d);
      setFindings(f.items || []);
      setRuns(r.items || []);
    } catch (e) {
      message.error(e.message || 'Không tải được Compliance Automation');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const seedRules = async () => {
    await api.seedComplianceAutomationRules();
    message.success('Đã nạp rule mặc định');
    load();
  };

  const runAll = async () => {
    setLoading(true);
    try {
      const result = await api.runComplianceAutomation({ scope: 'ALL_PROFILES' });
      message.success(`Đã chạy automation: ${result.run.total_findings} phát hiện`);
      load();
    } catch (e) {
      message.error(e.message || 'Không chạy được automation');
      setLoading(false);
    }
  };

  const findingColumns = [
    { title: 'Hồ sơ', dataIndex: 'profile_id', width: 90 },
    { title: 'Rule', dataIndex: 'rule_code', width: 180 },
    { title: 'Loại', dataIndex: 'finding_type', width: 160 },
    { title: 'Mức', dataIndex: 'severity', width: 100, render: v => <Tag color={sevColor(v)}>{v}</Tag> },
    { title: 'Tiêu đề', dataIndex: 'title' },
    { title: 'Khuyến nghị', dataIndex: 'recommendation' },
    { title: 'Trạng thái', dataIndex: 'status', width: 110, render: v => <Tag>{v}</Tag> },
  ];

  const runColumns = [
    { title: 'Run code', dataIndex: 'run_code' },
    { title: 'Scope', dataIndex: 'scope', width: 130 },
    { title: 'Hồ sơ', dataIndex: 'total_profiles', width: 90 },
    { title: 'Findings', dataIndex: 'total_findings', width: 100 },
    { title: 'High', dataIndex: 'high_findings', width: 80 },
    { title: 'Critical', dataIndex: 'critical_findings', width: 90 },
    { title: 'Readiness', dataIndex: 'readiness_score', width: 110, render: v => `${v}%` },
  ];

  return (
    <div>
      <PageHeader title="Compliance Automation" subtitle="Tự động kiểm tra gap, minh chứng, rủi ro và rà soát định kỳ" />
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<RobotOutlined />} onClick={seedRules}>Nạp rule mặc định</Button>
        <Button type="primary" icon={<ThunderboltOutlined />} onClick={runAll} loading={loading}>Chạy tự động toàn bộ hồ sơ</Button>
      </Space>

      {dashboard?.recommendations?.map((r, idx) => <Alert key={idx} type="info" showIcon message={r} style={{ marginBottom: 12 }} />)}

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={4}><Card><Statistic title="Rules" value={dashboard?.total_rules || 0} /></Card></Col>
        <Col span={4}><Card><Statistic title="Rules bật" value={dashboard?.enabled_rules || 0} /></Card></Col>
        <Col span={4}><Card><Statistic title="Runs" value={dashboard?.total_runs || 0} /></Card></Col>
        <Col span={4}><Card><Statistic title="Open findings" value={dashboard?.open_findings || 0} /></Card></Col>
        <Col span={4}><Card><Statistic title="High" value={dashboard?.high_findings || 0} /></Card></Col>
        <Col span={4}><Card><Statistic title="Critical" value={dashboard?.critical_findings || 0} /></Card></Col>
      </Row>

      <Card title="Phát hiện tự động" style={{ marginBottom: 16 }}>
        <Table rowKey="id" loading={loading} dataSource={findings} columns={findingColumns} pagination={{ pageSize: 10 }} />
      </Card>
      <Card title="Lịch sử chạy automation">
        <Table rowKey="id" loading={loading} dataSource={runs} columns={runColumns} pagination={{ pageSize: 5 }} />
      </Card>
    </div>
  );
}
