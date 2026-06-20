import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, Modal, Row, Select, Space, Statistic, Table, Tag, message } from 'antd';
import PageHeader from '../components/PageHeader';
import { api } from '../api/client';

const statusColor = { DRAFT: 'default', SUBMITTED: 'blue', COMMENTED: 'orange', COMPLETED: 'green' };
const severityColor = { LOW: 'green', MEDIUM: 'gold', HIGH: 'orange', CRITICAL: 'red' };

export default function AssessmentPortalPage({ profiles = [] }) {
  const [summary, setSummary] = useState(null);
  const [cases, setCases] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [caseOpen, setCaseOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [caseForm] = Form.useForm();
  const [feedbackForm] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const [s, c, f] = await Promise.all([
        api.assessmentPortalSummary(),
        api.assessmentCases({ limit: 100 }),
        api.assessmentFeedbacks({ limit: 100 }),
      ]);
      setSummary(s); setCases(c.items || []); setFeedbacks(f.items || []);
    } catch (e) { message.error(e.message || 'Không tải được cổng thẩm định'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const createCase = async () => {
    const v = await caseForm.validateFields();
    await api.createAssessmentCase(v);
    message.success('Đã tạo hồ sơ gửi thẩm định');
    setCaseOpen(false); caseForm.resetFields(); load();
  };

  const createFeedback = async () => {
    const v = await feedbackForm.validateFields();
    const selectedCase = cases.find(c => c.id === v.case_id);
    if (selectedCase && !v.profile_id) v.profile_id = selectedCase.profile_id;
    await api.createAssessmentFeedback(v);
    message.success('Đã ghi nhận ý kiến thẩm định');
    setFeedbackOpen(false); feedbackForm.resetFields(); load();
  };

  const submitCase = async (id) => { await api.submitAssessmentCase(id); message.success('Đã gửi thẩm định'); load(); };
  const completeCase = async (id) => { await api.completeAssessmentCase(id); message.success('Đã hoàn tất thẩm định'); load(); };
  const respondFeedback = async (id) => { await api.respondAssessmentFeedback(id, { response: 'Đơn vị đã tiếp thu và cập nhật hồ sơ theo ý kiến thẩm định.', status: 'RESPONDED' }); message.success('Đã phản hồi ý kiến'); load(); };

  return <>
    <PageHeader title="Cổng thẩm định" subtitle="Quản lý gửi hồ sơ, tiếp nhận ý kiến thẩm định và phản hồi hoàn thiện hồ sơ" />
    <Row gutter={[16,16]}>
      <Col xs={24} md={6}><Card><Statistic title="Tổng hồ sơ thẩm định" value={summary?.total_cases || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Đã gửi" value={summary?.submitted_cases || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Có ý kiến" value={summary?.commented_cases || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Ý kiến mở" value={summary?.open_feedbacks || 0} /></Card></Col>
    </Row>

    {(summary?.critical_feedbacks || 0) > 0 && <Alert style={{ marginTop: 16 }} type="error" showIcon message={`Có ${summary.critical_feedbacks} ý kiến thẩm định mức CRITICAL cần xử lý ngay`} />}

    <Card style={{ marginTop: 16 }} title="Hồ sơ gửi thẩm định" extra={<Button type="primary" onClick={() => setCaseOpen(true)}>Tạo hồ sơ gửi thẩm định</Button>}>
      <Table rowKey="id" loading={loading} dataSource={cases} pagination={{ pageSize: 8 }} columns={[
        { title: 'Mã', dataIndex: 'case_code' },
        { title: 'Tiêu đề', dataIndex: 'title' },
        { title: 'Đơn vị thẩm định', dataIndex: 'assessment_unit' },
        { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={statusColor[v] || 'default'}>{v}</Tag> },
        { title: 'Ngày gửi', dataIndex: 'submitted_at', render: v => v ? new Date(v).toLocaleString() : '-' },
        { title: 'Thao tác', render: (_, r) => <Space>
          {r.status === 'DRAFT' && <Button size="small" onClick={() => submitCase(r.id)}>Gửi</Button>}
          {r.status !== 'COMPLETED' && <Button size="small" onClick={() => completeCase(r.id)}>Hoàn tất</Button>}
        </Space> }
      ]} />
    </Card>

    <Card style={{ marginTop: 16 }} title="Ý kiến thẩm định" extra={<Button onClick={() => setFeedbackOpen(true)}>Thêm ý kiến</Button>}>
      <Table rowKey="id" loading={loading} dataSource={feedbacks} pagination={{ pageSize: 8 }} columns={[
        { title: 'Tiêu đề', dataIndex: 'title' },
        { title: 'Loại', dataIndex: 'feedback_type' },
        { title: 'Mức', dataIndex: 'severity', render: v => <Tag color={severityColor[v] || 'default'}>{v}</Tag> },
        { title: 'Trạng thái', dataIndex: 'status' },
        { title: 'Nội dung', dataIndex: 'content', ellipsis: true },
        { title: 'Phản hồi', render: (_, r) => r.response ? <Tag color="green">Đã phản hồi</Tag> : <Button size="small" onClick={() => respondFeedback(r.id)}>Phản hồi mẫu</Button> }
      ]} />
    </Card>

    <Modal title="Tạo hồ sơ gửi thẩm định" open={caseOpen} onCancel={() => setCaseOpen(false)} onOk={createCase} width={760}>
      <Form form={caseForm} layout="vertical" initialValues={{ submission_method: 'PORTAL', status: 'DRAFT', assessment_unit: 'Đơn vị thẩm định chuyên môn' }}>
        <Row gutter={12}>
          <Col span={12}><Form.Item name="case_code" label="Mã hồ sơ thẩm định" rules={[{ required: true }]}><Input placeholder="TD-2026-001" /></Form.Item></Col>
          <Col span={12}><Form.Item name="profile_id" label="Hồ sơ cấp độ" rules={[{ required: true }]}><Select options={profiles.map(p => ({ value: p.id, label: p.profile_code }))} /></Form.Item></Col>
        </Row>
        <Form.Item name="title" label="Tiêu đề" rules={[{ required: true }]}><Input /></Form.Item>
        <Row gutter={12}>
          <Col span={12}><Form.Item name="assessment_unit" label="Đơn vị thẩm định"><Input /></Form.Item></Col>
          <Col span={12}><Form.Item name="contact_person" label="Đầu mối"><Input /></Form.Item></Col>
        </Row>
        <Form.Item name="summary" label="Tóm tắt"><Input.TextArea rows={3} /></Form.Item>
      </Form>
    </Modal>

    <Modal title="Thêm ý kiến thẩm định" open={feedbackOpen} onCancel={() => setFeedbackOpen(false)} onOk={createFeedback} width={760}>
      <Form form={feedbackForm} layout="vertical" initialValues={{ feedback_type: 'COMMENT', severity: 'MEDIUM', status: 'OPEN' }}>
        <Row gutter={12}>
          <Col span={12}><Form.Item name="case_id" label="Hồ sơ thẩm định" rules={[{ required: true }]}><Select options={cases.map(c => ({ value: c.id, label: c.case_code }))} /></Form.Item></Col>
          <Col span={12}><Form.Item name="profile_id" label="Hồ sơ cấp độ"><Select allowClear options={profiles.map(p => ({ value: p.id, label: p.profile_code }))} /></Form.Item></Col>
        </Row>
        <Row gutter={12}>
          <Col span={12}><Form.Item name="feedback_type" label="Loại"><Select options={['COMMENT','REQUEST_CHANGE','REQUIRE_EVIDENCE','RISK_NOTE'].map(x=>({value:x,label:x}))} /></Form.Item></Col>
          <Col span={12}><Form.Item name="severity" label="Mức"><Select options={['LOW','MEDIUM','HIGH','CRITICAL'].map(x=>({value:x,label:x}))} /></Form.Item></Col>
        </Row>
        <Form.Item name="title" label="Tiêu đề" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="content" label="Nội dung" rules={[{ required: true }]}><Input.TextArea rows={4} /></Form.Item>
      </Form>
    </Modal>
  </>;
}
