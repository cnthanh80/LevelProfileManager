import { Alert, Card, Col, Row, Statistic, Table, Typography } from 'antd';

export default function DashboardPage({ data }) {
  const summary = data.summary || {};
  const workflow = data.workflow || {};
  const compliance = data.compliance || {};
  const gaps = data.gaps || [];
  const enterprise = data.enterprise || {};
  const executive = data.executive || {};

  const gapRows = Array.isArray(gaps.items) ? gaps.items : Array.isArray(gaps) ? gaps : [];
  const levelRows = Array.isArray(executive.level_matrix) ? executive.level_matrix : [];
  const riskRows = Array.isArray(executive.top_risk_profiles) ? executive.top_risk_profiles : [];

  return (
    <>
      <Typography.Title level={3}>Dashboard quản trị</Typography.Title>
      {enterprise.executive_status === 'ATTENTION_REQUIRED' && (
        <Alert type="warning" showIcon message="Có hồ sơ hoặc tiêu chí cần lãnh đạo/cán bộ ATTT theo dõi" style={{ marginBottom: 16 }} />
      )}
      <Row gutter={[16, 16]}>
        <Col span={6}><Card><Statistic title="Tổng số HTTT" value={enterprise.total_systems ?? summary.total_systems ?? 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Tổng số hồ sơ" value={enterprise.total_profiles ?? summary.total_profiles ?? 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Cấp độ 3+" value={enterprise.level_3_or_above ?? summary.level_3_or_above ?? 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Thiếu minh chứng" value={enterprise.profiles_missing_evidence ?? summary.profiles_missing_evidence ?? 0} /></Card></Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={6}><Card><Statistic suffix="%" title="Điểm tuân thủ TB" value={Math.round(enterprise.average_compliance_score || compliance.overall_compliance_rate || 0)} /></Card></Col>
        <Col span={6}><Card><Statistic title="Điểm rủi ro TB" value={Math.round(enterprise.average_risk_score || 0)} /></Card></Col>
        <Col span={6}><Card><Statistic title="Tiêu chí bắt buộc thiếu" value={enterprise.mandatory_gap || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="Rà soát đến hạn 30 ngày" value={enterprise.review_due_30_days || 0} /></Card></Col>
      </Row>
      <Card title="Ma trận hệ thống/hồ sơ theo cấp độ" style={{ marginTop: 16 }}>
        <Table rowKey="level" dataSource={levelRows} pagination={false} columns={[
          { title: 'Cấp độ', dataIndex: 'level' },
          { title: 'Số HTTT', dataIndex: 'systems' },
          { title: 'Số hồ sơ', dataIndex: 'profiles' },
          { title: 'Trạng thái workflow', dataIndex: 'workflow_statuses', render: (v) => <pre style={{ margin: 0 }}>{JSON.stringify(v || {}, null, 2)}</pre> },
        ]} />
      </Card>
      <Card title="Top hồ sơ rủi ro/cần ưu tiên" style={{ marginTop: 16 }}>
        <Table rowKey="profile_id" dataSource={riskRows} pagination={false} columns={[
          { title: 'Hồ sơ', dataIndex: 'profile_code' },
          { title: 'Cấp độ', dataIndex: 'proposed_level' },
          { title: 'Tuân thủ', dataIndex: 'overall_score', render: (v) => `${v || 0}%` },
          { title: 'Gap', dataIndex: 'gap_total' },
          { title: 'Rủi ro', dataIndex: 'risk_level' },
          { title: 'Điểm rủi ro', dataIndex: 'risk_score' },
        ]} />
      </Card>
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
