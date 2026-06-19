import React from 'react';
import { Alert, Card, Col, Progress, Row, Statistic, Table, Typography } from 'antd';
import PageHeader from '../components/PageHeader';
import StatusTag from '../components/StatusTag';

function arr(x) { return Array.isArray(x?.items) ? x.items : Array.isArray(x) ? x : []; }

export default function DashboardPage({ data }) {
  const summary = data.summary || {}, workflow = data.workflow || {}, compliance = data.compliance || {}, enterprise = data.enterprise || {}, executive = data.executive || {};
  const gapRows = arr(data.gaps);
  const levelRows = arr(data.levelMatrix?.items || data.levelMatrix || executive.level_matrix);
  const actionRows = arr(data.actionBoard?.items || data.actionBoard || executive.top_risk_profiles);

  return (
    <>
      <PageHeader title="Dashboard điều hành" subtitle="Tổng quan hệ thống thông tin, hồ sơ cấp độ, tuân thủ, rủi ro và rà soát định kỳ." />
      {(enterprise.executive_status === 'ATTENTION_REQUIRED' || summary.alerts) && <Alert type="warning" showIcon message="Có hồ sơ cần theo dõi hoặc bổ sung minh chứng" style={{ marginBottom: 16 }} />}
      <Row gutter={[16,16]}>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Tổng số HTTT" value={enterprise.total_systems ?? summary.total_systems ?? 0} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Tổng số hồ sơ" value={enterprise.total_profiles ?? summary.total_profiles ?? 0} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Hệ thống cấp độ 3+" value={enterprise.level_3_or_above ?? summary.level_3_or_above ?? 0} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Thiếu minh chứng" value={enterprise.profiles_missing_evidence ?? summary.profiles_missing_evidence ?? 0} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Đến hạn rà soát 30 ngày" value={enterprise.review_due_30_days ?? data.reviewDashboard?.due_soon ?? 0} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Tiêu chí bắt buộc thiếu" value={enterprise.mandatory_gap ?? 0} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic suffix="%" title="Tuân thủ TB" value={Math.round(enterprise.average_compliance_score || compliance.overall_compliance_rate || 0)} /></Card></Col>
        <Col xs={24} md={12} xl={6}><Card><Statistic title="Rủi ro TB" value={Math.round(enterprise.average_risk_score || 0)} /></Card></Col>
      </Row>
      <Row gutter={[16,16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={8}><Card title="Compliance"><Progress type="dashboard" percent={Math.round(enterprise.average_compliance_score || compliance.overall_compliance_rate || 0)} /><Typography.Paragraph type="secondary">Tỷ lệ đáp ứng trung bình trên các hồ sơ.</Typography.Paragraph></Card></Col>
        <Col xs={24} lg={8}><Card title="Readiness"><Progress type="dashboard" percent={Math.round(data.complianceDashboard?.average_readiness_score || enterprise.average_readiness_score || 0)} /><Typography.Paragraph type="secondary">Mức sẵn sàng gửi thẩm định.</Typography.Paragraph></Card></Col>
        <Col xs={24} lg={8}><Card title="Workflow"><pre style={{ margin: 0, maxHeight: 220, overflow: 'auto' }}>{JSON.stringify(workflow, null, 2)}</pre></Card></Col>
      </Row>
      <Card title="Ma trận theo cấp độ" style={{ marginTop: 16 }}>
        <Table rowKey={(r) => r.level || JSON.stringify(r)} dataSource={levelRows} pagination={false} columns={[
          { title: 'Cấp độ', dataIndex: 'level', render: (v) => <StatusTag value={`Level ${v}`} /> },
          { title: 'Số HTTT', dataIndex: 'systems' }, { title: 'Số hồ sơ', dataIndex: 'profiles' },
          { title: 'Workflow', dataIndex: 'workflow_statuses', render: (v) => <pre style={{ margin: 0 }}>{JSON.stringify(v || {}, null, 2)}</pre> }
        ]} />
      </Card>
      <Card title="Action board / hồ sơ rủi ro" style={{ marginTop: 16 }}>
        <Table rowKey={(r) => r.profile_id || r.id || JSON.stringify(r)} dataSource={actionRows} columns={[
          { title: 'Hồ sơ', dataIndex: 'profile_code' }, { title: 'Cấp độ', dataIndex: 'proposed_level' },
          { title: 'Tuân thủ', dataIndex: 'overall_score', render: (v) => v !== undefined ? `${v}%` : '—' },
          { title: 'Gap', dataIndex: 'gap_total' }, { title: 'Rủi ro', dataIndex: 'risk_level', render: (v) => <StatusTag value={v} /> }, { title: 'Điểm', dataIndex: 'risk_score' }
        ]} />
      </Card>
      <Card title="Hồ sơ thiếu minh chứng" style={{ marginTop: 16 }}>
        <Table rowKey={(r) => r.profile_id || r.id || JSON.stringify(r)} dataSource={gapRows} columns={[
          { title: 'Hồ sơ', dataIndex: 'profile_name' }, { title: 'Hệ thống', dataIndex: 'system_name' },
          { title: 'Cấp độ', dataIndex: 'proposed_level' }, { title: 'Số tiêu chí thiếu', dataIndex: 'missing_evidence_count' }
        ]} />
      </Card>
    </>
  );
}
