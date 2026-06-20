import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, Row, Select, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

const statusColors = {
  DRAFT: 'default', SECURITY_REVIEW: 'blue', INTERNAL_REVISION_REQUIRED: 'orange', READY_FOR_EXTERNAL_ASSESSMENT: 'cyan',
  SENT_TO_ASSESSMENT_UNIT: 'purple', ASSESSMENT_COMMENTS_RECEIVED: 'gold', CLARIFICATION_REQUIRED: 'volcano',
  CLARIFICATION_SUBMITTED: 'geekblue', ASSESSMENT_APPROVED: 'green', ASSESSMENT_REJECTED: 'red', APPROVAL_DECISION_ISSUED: 'green'
};

export default function AssessmentWorkflowPage() {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [rules, setRules] = useState([]);
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [events, setEvents] = useState([]);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const [sum, r, c] = await Promise.all([
        api.assessmentWorkflowSummary(), api.assessmentWorkflowRules(), api.assessmentCases({ limit: 200 })
      ]);
      setSummary(sum); setRules(r || []); setCases(c.items || []);
      if (!selectedCase && c.items?.length) setSelectedCase(c.items[0]);
    } catch (e) { message.error(e.message || 'Không tải được workflow thẩm định'); }
    finally { setLoading(false); }
  };

  const loadEvents = async (caseId) => {
    if (!caseId) return;
    try { setEvents(await api.assessmentWorkflowEvents(caseId)); } catch (e) { setEvents([]); }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => { if (selectedCase?.id) loadEvents(selectedCase.id); }, [selectedCase?.id]);

  const validActions = rules.filter(r => r.from_status === (selectedCase?.status || 'DRAFT'));

  const doTransition = async (values) => {
    if (!selectedCase) return;
    try {
      const res = await api.transitionAssessmentWorkflow(selectedCase.id, values);
      message.success(`Đã chuyển trạng thái: ${res.current_status}`);
      form.resetFields();
      await load();
      const refreshed = await api.assessmentCases({ limit: 200 });
      const next = (refreshed.items || []).find(x => x.id === selectedCase.id);
      setSelectedCase(next || selectedCase);
      await loadEvents(selectedCase.id);
    } catch (e) { message.error(e.message || 'Chuyển trạng thái thất bại'); }
  };

  return <div>
    <PageHeader title="Workflow thẩm định đa cấp" subtitle="Quản lý quy trình gửi thẩm định, nhận ý kiến, giải trình và ban hành quyết định phê duyệt" />
    <Row gutter={[16, 16]}>
      <Col xs={24} md={6}><Card><Statistic title="Tổng hồ sơ thẩm định" value={summary?.total_cases || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Chờ gửi/đang thẩm định" value={summary?.pending_external_assessment || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Chờ giải trình" value={summary?.waiting_for_clarification || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Quá hạn" value={summary?.overdue_cases || 0} /></Card></Col>
    </Row>

    <Card title="Chọn hồ sơ thẩm định" style={{ marginTop: 16 }} extra={<Button onClick={load}>Tải lại</Button>}>
      <Table loading={loading} rowKey="id" dataSource={cases} pagination={{ pageSize: 6 }} onRow={(record) => ({ onClick: () => setSelectedCase(record) })}
        columns={[
          { title: 'Mã', dataIndex: 'case_code' },
          { title: 'Tiêu đề', dataIndex: 'title' },
          { title: 'Đơn vị thẩm định', dataIndex: 'assessment_unit' },
          { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={statusColors[v] || 'default'}>{v}</Tag> },
        ]} />
    </Card>

    {selectedCase && <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
      <Col xs={24} lg={10}>
        <Card title={`Chuyển trạng thái: ${selectedCase.case_code}`}>
          <Alert showIcon type="info" message="Trạng thái hiện tại" description={<Tag color={statusColors[selectedCase.status] || 'default'}>{selectedCase.status}</Tag>} style={{ marginBottom: 16 }} />
          <Form form={form} layout="vertical" onFinish={doTransition}>
            <Form.Item name="action" label="Hành động" rules={[{ required: true }]}>
              <Select placeholder="Chọn hành động hợp lệ" options={validActions.map(r => ({ value: r.action, label: `${r.action} → ${r.to_status}` }))} />
            </Form.Item>
            <Form.Item name="assessment_unit" label="Đơn vị thẩm định"><Input placeholder="Ví dụ: Cục ATTT / Đơn vị thẩm định độc lập" /></Form.Item>
            <Form.Item name="external_reference" label="Số văn bản/phiếu xử lý"><Input /></Form.Item>
            <Form.Item name="comment" label="Ý kiến xử lý"><Input.TextArea rows={4} /></Form.Item>
            <Button type="primary" htmlType="submit">Thực hiện chuyển trạng thái</Button>
          </Form>
        </Card>
      </Col>
      <Col xs={24} lg={14}>
        <Card title="Lịch sử workflow thẩm định">
          <Table rowKey="id" dataSource={events} pagination={{ pageSize: 6 }} columns={[
            { title: 'Thời gian', dataIndex: 'occurred_at' },
            { title: 'Hành động', dataIndex: 'action' },
            { title: 'Từ', dataIndex: 'from_status' },
            { title: 'Đến', dataIndex: 'to_status', render: v => <Tag color={statusColors[v] || 'default'}>{v}</Tag> },
            { title: 'Ý kiến', dataIndex: 'comment' },
          ]} />
        </Card>
      </Col>
    </Row>}

    <Card title="Quy tắc workflow" style={{ marginTop: 16 }}>
      <JsonView value={rules} />
    </Card>
  </div>;
}
