import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Descriptions, Empty, List, Progress, Row, Space, Spin, Statistic, Table, Tag, Typography } from 'antd';
import { CrownOutlined, ReloadOutlined } from '@ant-design/icons';
import { api } from '../api/client';

const statusColor = {
  NORMAL: 'green',
  WATCH: 'blue',
  ATTENTION_REQUIRED: 'orange',
  CRITICAL: 'red',
};

function rowsFromDict(obj = {}) {
  return Object.entries(obj || {}).map(([name, value]) => ({ name, value }));
}

export default function ExecutiveDashboardPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [board, setBoard] = useState(null);

  const load = async () => {
    setLoading(true); setError('');
    try {
      setBoard(await api.executiveBoardPack());
    } catch (e) {
      setError(e.message || 'Không tải được Executive Dashboard');
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  if (loading && !board) return <div style={{ padding: 80, textAlign: 'center' }}><Spin size="large" /></div>;
  if (error) return <Alert type="error" showIcon message="Lỗi Executive Dashboard" description={error} action={<Button onClick={load}>Tải lại</Button>} />;
  if (!board) return <Empty description="Chưa có dữ liệu dashboard lãnh đạo" />;

  const k = board.kpis || {};
  const portfolio = board.portfolio || {};
  const actions = board.priority_actions || {};

  const smallTableCols = [
    { title: 'Nhóm', dataIndex: 'name', key: 'name' },
    { title: 'Số lượng', dataIndex: 'value', key: 'value', width: 120, render: (v) => <b>{v}</b> },
  ];

  return <Space direction="vertical" size="large" style={{ width: '100%' }}>
    <Card>
      <Row justify="space-between" align="middle" gutter={[16, 16]}>
        <Col>
          <Typography.Title level={3} style={{ margin: 0 }}><CrownOutlined /> Dashboard lãnh đạo</Typography.Title>
          <Typography.Text type="secondary">Tổng hợp tình hình hồ sơ đề xuất cấp độ, rủi ro, tuân thủ và thẩm định</Typography.Text>
        </Col>
        <Col>
          <Space>
            <Tag color={statusColor[k.executive_status] || 'default'}>{k.executive_status}</Tag>
            <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>Làm mới</Button>
          </Space>
        </Col>
      </Row>
    </Card>

    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Tổng HTTT" value={k.total_systems || 0} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="HTTT cấp độ 3+" value={k.level3_plus_systems || 0} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Tổng hồ sơ" value={k.total_profiles || 0} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Tỷ lệ phê duyệt" value={k.approval_rate || 0} suffix="%" /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Gap bắt buộc" value={k.mandatory_gap || 0} valueStyle={{ color: (k.mandatory_gap || 0) ? '#cf1322' : undefined }} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Thiếu minh chứng" value={k.profiles_missing_evidence || 0} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Rủi ro cao" value={k.high_risks || 0} valueStyle={{ color: (k.high_risks || 0) ? '#cf1322' : undefined }} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Quá hạn rà soát" value={k.overdue_reviews || 0} valueStyle={{ color: (k.overdue_reviews || 0) ? '#cf1322' : undefined }} /></Card></Col>
    </Row>

    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <Card title="Mức độ tuân thủ trung bình">
          <Progress type="dashboard" percent={Math.round(k.average_compliance || 0)} />
          <Descriptions column={1} size="small" style={{ marginTop: 16 }}>
            <Descriptions.Item label="Điểm rủi ro trung bình">{k.average_risk_score || 0}</Descriptions.Item>
            <Descriptions.Item label="Điểm cảnh báo điều hành">{k.severity_score || 0}</Descriptions.Item>
            <Descriptions.Item label="Hồ sơ thẩm định đang xử lý">{k.pending_assessment_cases || 0}</Descriptions.Item>
            <Descriptions.Item label="Ý kiến thẩm định chưa đóng">{k.open_assessment_feedbacks || 0}</Descriptions.Item>
          </Descriptions>
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Khuyến nghị điều hành">
          <List dataSource={board.recommendations || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
        </Card>
      </Col>
    </Row>

    <Row gutter={[16, 16]}>
      <Col xs={24} lg={8}><Card title="HTTT theo cấp độ"><Table size="small" pagination={false} rowKey="name" columns={smallTableCols} dataSource={rowsFromDict(portfolio.systems_by_level)} /></Card></Col>
      <Col xs={24} lg={8}><Card title="Hồ sơ theo trạng thái"><Table size="small" pagination={false} rowKey="name" columns={smallTableCols} dataSource={rowsFromDict(portfolio.profiles_by_status)} /></Card></Col>
      <Col xs={24} lg={8}><Card title="Rủi ro theo mức"><Table size="small" pagination={false} rowKey="name" columns={smallTableCols} dataSource={rowsFromDict(portfolio.risks_by_level)} /></Card></Col>
    </Row>

    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <Card title="Top rủi ro cần xử lý">
          <Table size="small" rowKey="id" pagination={false} dataSource={actions.top_risks || []} columns={[
            { title: 'Mã', dataIndex: 'code' },
            { title: 'Rủi ro', dataIndex: 'title' },
            { title: 'Mức', dataIndex: 'risk_level', render: (v, r) => <Tag color={r.risk_color}>{v}</Tag> },
            { title: 'Điểm', dataIndex: 'risk_score', width: 80 },
          ]} />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Gap bắt buộc ưu tiên">
          <Table size="small" rowKey="id" pagination={false} dataSource={actions.mandatory_gaps || []} columns={[
            { title: 'Hồ sơ', dataIndex: 'profile_code' },
            { title: 'Yêu cầu', dataIndex: 'requirement_code' },
            { title: 'Nội dung', dataIndex: 'title' },
            { title: 'Hạn', dataIndex: 'due_date', width: 110 },
          ]} />
        </Card>
      </Col>
    </Row>
  </Space>;
}
