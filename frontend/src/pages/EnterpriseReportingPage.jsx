import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Row, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { api, downloadFile } from '../api/client';

export default function EnterpriseReportingPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try { setData(await api.enterpriseReportingDashboard()); }
    catch (e) { setError(e.message || 'Không tải được dữ liệu reporting'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const generate = async () => {
    setLoading(true); setError('');
    try { await api.generateEnterpriseReportSnapshot({ period_type: 'MONTHLY', refresh_metrics: true }); await load(); }
    catch (e) { setError(e.message || 'Không sinh được snapshot'); }
    finally { setLoading(false); }
  };


  const downloadPortfolio = async () => {
    try { const r = await downloadFile(api.enterprisePortfolioCsvUrl(), 'enterprise-portfolio.csv'); message.success(`Đã tải: ${r.filename}`); }
    catch (e) { message.error(e.message || 'Không tải được CSV danh mục'); }
  };

  const summary = data?.summary || {};
  const dist = summary.level_distribution || {};
  return <Space direction="vertical" size="large" style={{ width: '100%' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <div>
        <Typography.Title level={3}>Enterprise Reporting & Data Warehouse</Typography.Title>
        <Typography.Text type="secondary">Báo cáo điều hành, dữ liệu tổng hợp và snapshot danh mục hồ sơ cấp độ.</Typography.Text>
      </div>
      <Space>
        <Button onClick={load}>Tải lại</Button>
        <Button type="primary" onClick={generate}>Sinh snapshot</Button>
        <Button onClick={downloadPortfolio}>Tải CSV danh mục</Button>
      </Space>
    </div>
    {error && <Alert type="error" showIcon message={error} />}
    <Row gutter={[16,16]}>
      <Col xs={24} md={6}><Card><Statistic title="Hệ thống" value={summary.total_systems || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Hồ sơ" value={summary.total_profiles || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Điểm tuân thủ TB" value={summary.portfolio_average_score || 0} suffix="/100" /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Rủi ro cao" value={summary.high_risk_count || 0} /></Card></Col>
    </Row>
    <Card title="Phân bố cấp độ">
      <Space wrap>{[1,2,3,4,5].map(l => <Tag key={l} color={l >= 3 ? 'red' : 'blue'}>Cấp độ {l}: {dist[String(l)] || 0}</Tag>)}</Space>
    </Card>
    <Card title="Snapshot gần đây">
      <Table loading={loading} rowKey="id" dataSource={data?.recent_snapshots || []} pagination={{ pageSize: 5 }} columns={[
        { title: 'Mã snapshot', dataIndex: 'snapshot_code' },
        { title: 'Kỳ', dataIndex: 'period_label' },
        { title: 'Hồ sơ', dataIndex: 'total_profiles' },
        { title: 'Điểm TB', dataIndex: 'overall_compliance_score' },
        { title: 'Rủi ro cao', dataIndex: 'high_risk_count' },
      ]} />
    </Card>
    <Card title="Data Warehouse Metrics">
      <Table loading={loading} rowKey="id" dataSource={data?.data_warehouse_metrics || []} pagination={{ pageSize: 10 }} columns={[
        { title: 'Nhóm', dataIndex: 'metric_group' },
        { title: 'Mã', dataIndex: 'metric_code' },
        { title: 'Chỉ số', dataIndex: 'metric_name' },
        { title: 'Giá trị', dataIndex: 'metric_value' },
        { title: 'Chiều dữ liệu', render: (_, r) => r.dimension_key ? `${r.dimension_key}: ${r.dimension_value}` : '-' },
      ]} />
    </Card>
    <Card title="Khuyến nghị điều hành">
      {(summary.recommendations || []).map((x, i) => <Alert key={i} style={{ marginBottom: 8 }} type="info" showIcon message={x} />)}
    </Card>
  </Space>;
}
