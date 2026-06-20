import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Row, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { LineChartOutlined, RadarChartOutlined, SyncOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import { api } from '../api/client';

function riskColor(risk) {
  if (risk === 'CRITICAL') return 'red';
  if (risk === 'HIGH') return 'volcano';
  if (risk === 'MEDIUM') return 'orange';
  return 'green';
}

function heatColor(color) {
  if (color === 'RED') return 'red';
  if (color === 'ORANGE') return 'volcano';
  if (color === 'YELLOW') return 'gold';
  return 'green';
}

export default function ComplianceMonitoringPage({ profiles = [] }) {
  const [dashboard, setDashboard] = useState(null);
  const [heatmap, setHeatmap] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [findings, setFindings] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [d, h, s, f, n] = await Promise.all([
        api.complianceMonitoringDashboard(),
        api.complianceMonitoringHeatmap(),
        api.complianceMonitoringSnapshots({ limit: 20 }),
        api.complianceMonitoringFindings({ limit: 30 }),
        api.complianceMonitoringNotifications({ limit: 20 }),
      ]);
      setDashboard(d);
      setHeatmap(Array.isArray(h) ? h : []);
      setSnapshots(s.items || []);
      setFindings(f.items || []);
      setNotifications(n.items || []);
    } catch (e) {
      message.error(e.message || 'Không tải được Continuous Compliance Monitoring');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const runMonitoring = async () => {
    setLoading(true);
    try {
      const result = await api.runComplianceMonitoring({ scope: 'ALL_PROFILES', create_notifications: true });
      message.success(`Đã tạo ${result.snapshots_created} snapshot, ${result.findings_created} finding`);
      await load();
    } catch (e) {
      message.error(e.message || 'Không chạy được monitoring');
      setLoading(false);
    }
  };

  const heatColumns = [
    { title: 'Hồ sơ', dataIndex: 'profile_code', width: 150 },
    { title: 'Hệ thống', dataIndex: 'system_name' },
    { title: 'Đơn vị', dataIndex: 'organization_name' },
    { title: 'Cấp độ', dataIndex: 'proposed_level', width: 80 },
    { title: 'Score', dataIndex: 'overall_score', width: 100, render: v => <b>{v}%</b> },
    { title: 'Risk', dataIndex: 'risk_level', width: 120, render: v => <Tag color={riskColor(v)}>{v}</Tag> },
    { title: 'Heat', dataIndex: 'heat_color', width: 100, render: v => <Tag color={heatColor(v)}>{v}</Tag> },
    { title: 'Mandatory gap', dataIndex: 'mandatory_gap_count', width: 130 },
    { title: 'Thiếu MC', dataIndex: 'missing_evidence_count', width: 100 },
    { title: 'Finding mở', dataIndex: 'open_finding_count', width: 110 },
  ];

  const snapshotColumns = [
    { title: 'Snapshot', dataIndex: 'snapshot_code', width: 190 },
    { title: 'Hồ sơ', dataIndex: 'profile_code', width: 150 },
    { title: 'Mgmt', dataIndex: 'management_score', width: 80, render: v => `${v}%` },
    { title: 'Tech', dataIndex: 'technical_score', width: 80, render: v => `${v}%` },
    { title: 'Evidence', dataIndex: 'evidence_score', width: 90, render: v => `${v}%` },
    { title: 'Overall', dataIndex: 'overall_score', width: 90, render: v => <b>{v}%</b> },
    { title: 'Risk', dataIndex: 'risk_level', width: 100, render: v => <Tag color={riskColor(v)}>{v}</Tag> },
    { title: 'Trend', dataIndex: 'trend_direction', width: 100, render: v => <Tag>{v}</Tag> },
  ];

  const findingColumns = [
    { title: 'Hồ sơ', dataIndex: 'profile_id', width: 90 },
    { title: 'Loại', dataIndex: 'finding_type', width: 160 },
    { title: 'Mức', dataIndex: 'severity', width: 100, render: v => <Tag color={riskColor(v)}>{v}</Tag> },
    { title: 'Tiêu đề', dataIndex: 'title' },
    { title: 'Khuyến nghị', dataIndex: 'recommendation' },
    { title: 'Trạng thái', dataIndex: 'status', width: 110, render: v => <Tag>{v}</Tag> },
  ];

  return (
    <div>
      <PageHeader title="Continuous Compliance Monitoring" subtitle="Giám sát tuân thủ liên tục theo checklist, minh chứng, automation findings và xu hướng rủi ro" />
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<SyncOutlined />} loading={loading} onClick={runMonitoring}>Chạy monitoring toàn bộ hồ sơ</Button>
        <Button icon={<LineChartOutlined />} onClick={load}>Tải lại</Button>
      </Space>

      {dashboard?.recommendations?.map((r, idx) => <Alert key={idx} type="info" showIcon message={r} style={{ marginBottom: 12 }} />)}

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={5}><Card><Statistic title="Portfolio score" value={dashboard?.portfolio_average_score || 0} suffix="%" /></Card></Col>
        <Col span={5}><Card><Statistic title="Hồ sơ giám sát" value={dashboard?.total_profiles_monitored || 0} /></Card></Col>
        <Col span={5}><Card><Statistic title="High/Critical" value={dashboard?.high_risk_profiles || 0} /></Card></Col>
        <Col span={5}><Card><Statistic title="Open findings" value={dashboard?.open_findings || 0} /></Card></Col>
        <Col span={4}><Card><Statistic title="Notifications" value={dashboard?.notifications || 0} /></Card></Col>
      </Row>

      <Card title={<Space><RadarChartOutlined />Compliance Risk Heatmap</Space>} style={{ marginBottom: 16 }}>
        <Table rowKey="profile_id" loading={loading} dataSource={heatmap} columns={heatColumns} pagination={{ pageSize: 8 }} scroll={{ x: 1100 }} />
      </Card>

      <Card title="Snapshot gần nhất" style={{ marginBottom: 16 }}>
        <Table rowKey="id" loading={loading} dataSource={snapshots} columns={snapshotColumns} pagination={{ pageSize: 8 }} scroll={{ x: 900 }} />
      </Card>

      <Card title="Findings từ monitoring" style={{ marginBottom: 16 }}>
        <Table rowKey="id" loading={loading} dataSource={findings} columns={findingColumns} pagination={{ pageSize: 8 }} scroll={{ x: 1000 }} />
      </Card>

      <Card title="Thông báo monitoring">
        <Table rowKey="id" loading={loading} dataSource={notifications} pagination={{ pageSize: 5 }} columns={[
          { title: 'Event', dataIndex: 'event_type', width: 200 },
          { title: 'Kênh', dataIndex: 'channel', width: 100 },
          { title: 'Người nhận', dataIndex: 'recipient', width: 160 },
          { title: 'Subject', dataIndex: 'subject' },
          { title: 'Trạng thái', dataIndex: 'status', width: 120, render: v => <Tag>{v}</Tag> },
        ]} />
      </Card>
    </div>
  );
}
