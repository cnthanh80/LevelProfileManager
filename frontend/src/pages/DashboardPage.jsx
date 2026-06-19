import { Card, Col, Row, Statistic, Table, Typography } from 'antd';

export default function DashboardPage({ data }) {
  const summary = data.summary || {};
  const workflow = data.workflow || {};
  const compliance = data.compliance || {};
  const gaps = data.gaps || [];

  const gapRows = Array.isArray(gaps.items) ? gaps.items : Array.isArray(gaps) ? gaps : [];

  return (
    <>
      <Typography.Title level={3}>Dashboard quản trị</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Statistic title="Tổng số HTTT" value={summary.total_systems || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Tổng số hồ sơ" value={summary.total_profiles || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Cấp độ 3+" value={summary.level_3_or_above || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Thiếu minh chứng" value={summary.profiles_missing_evidence || 0} /></Card></Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={8}><Card title="Tỷ lệ đáp ứng tổng"><Statistic suffix="%" value={Math.round(compliance.overall_compliance_rate || 0)} /></Card></Col>
        <Col span={8}><Card title="Đáp ứng quản lý"><Statistic suffix="%" value={Math.round(compliance.management_compliance_rate || 0)} /></Card></Col>
        <Col span={8}><Card title="Đáp ứng kỹ thuật"><Statistic suffix="%" value={Math.round(compliance.technical_compliance_rate || 0)} /></Card></Col>
      </Row>
      <Card title="Hồ sơ theo trạng thái workflow" style={{ marginTop: 16 }}>
        <pre style={{ margin: 0 }}>{JSON.stringify(workflow, null, 2)}</pre>
      </Card>
      <Card title="Hồ sơ thiếu minh chứng" style={{ marginTop: 16 }}>
        <Table rowKey={(r) => r.profile_id || r.id} dataSource={gapRows} pagination={false} columns={[
          { title: 'Hồ sơ', dataIndex: 'profile_name' },
          { title: 'Hệ thống', dataIndex: 'system_name' },
          { title: 'Cấp độ', dataIndex: 'proposed_level' },
          { title: 'Số tiêu chí thiếu', dataIndex: 'missing_evidence_count' },
        ]} />
      </Card>
    </>
  );
}
