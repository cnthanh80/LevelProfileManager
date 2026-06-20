import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Form, Input, InputNumber, Modal, Row, Select, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import PageHeader from '../components/PageHeader';
import { api } from '../api/client';

const levelColor = { LOW: 'green', MEDIUM: 'gold', HIGH: 'orange', CRITICAL: 'red' };

export default function RiskSlaPage({ profiles = [], systems = [] }) {
  const [summary, setSummary] = useState(null);
  const [risks, setRisks] = useState([]);
  const [sla, setSla] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [rs, rl, ss, sp] = await Promise.all([
        api.riskRegisterSummary(), api.riskRegisters({ limit: 100 }), api.slaSummary(), api.slaPolicies({ limit: 100 })
      ]);
      setSummary(rs); setRisks(rl.items || []); setSla(ss); setPolicies(sp.items || []);
    } catch (e) { message.error(e.message || 'Không tải được Risk/SLA'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const submit = async () => {
    const v = await form.validateFields();
    await api.createRiskRegister(v);
    message.success('Đã tạo rủi ro');
    setOpen(false); form.resetFields(); load();
  };

  const seedSla = async () => { await api.seedSlaPolicies(); message.success('Đã seed SLA mặc định'); load(); };

  return <>
    <PageHeader title="SLA & Risk Register" subtitle="Quản lý danh mục rủi ro, SLA xử lý hồ sơ và cảnh báo tồn đọng" />
    <Row gutter={[16,16]}>
      <Col xs={24} md={6}><Card><Statistic title="Tổng rủi ro" value={summary?.total || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Rủi ro đang mở" value={summary?.open_items || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Critical/High" value={(summary?.critical_items || 0) + (summary?.high_items || 0)} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="SLA breached" value={sla?.breached_items || 0} /></Card></Col>
    </Row>

    <Card style={{ marginTop: 16 }} title="Risk Register" extra={<Button type="primary" onClick={() => setOpen(true)}>Thêm rủi ro</Button>}>
      <Table rowKey="id" loading={loading} dataSource={risks} pagination={{ pageSize: 8 }} columns={[
        { title: 'Mã', dataIndex: 'risk_code' },
        { title: 'Rủi ro', dataIndex: 'title' },
        { title: 'Nhóm', dataIndex: 'category' },
        { title: 'Điểm', dataIndex: 'risk_score' },
        { title: 'Mức', dataIndex: 'risk_level', render: v => <Tag color={levelColor[v] || 'default'}>{v}</Tag> },
        { title: 'Trạng thái', dataIndex: 'status' },
        { title: 'Phụ trách', dataIndex: 'owner' },
      ]} />
    </Card>

    <Card style={{ marginTop: 16 }} title="SLA Workflow" extra={<Button onClick={seedSla}>Seed SLA mặc định</Button>}>
      {sla?.items?.length ? <Alert type="warning" showIcon message={`Có ${sla.items.length} hồ sơ cần chú ý theo SLA`} style={{ marginBottom: 12 }} /> : <Alert type="success" showIcon message="Không có hồ sơ vi phạm SLA" style={{ marginBottom: 12 }} />}
      <Table rowKey={(r) => `${r.profile_id}-${r.current_status}`} dataSource={sla?.items || []} pagination={{ pageSize: 5 }} columns={[
        { title: 'Hồ sơ', dataIndex: 'profile_code' },
        { title: 'Trạng thái', dataIndex: 'current_status' },
        { title: 'Tuổi xử lý (giờ)', dataIndex: 'age_hours' },
        { title: 'SLA (giờ)', dataIndex: 'due_hours' },
        { title: 'Mức', dataIndex: 'severity', render: v => <Tag color={levelColor[v] || 'blue'}>{v}</Tag> },
        { title: 'Tình trạng', dataIndex: 'state', render: v => <Tag color={v === 'BREACHED' ? 'red' : 'orange'}>{v}</Tag> },
      ]} />
      <Typography.Title level={5}>Chính sách SLA</Typography.Title>
      <Table size="small" rowKey="id" dataSource={policies} pagination={false} columns={[
        { title: 'Mã', dataIndex: 'code' }, { title: 'Tên', dataIndex: 'name' }, { title: 'Workflow', dataIndex: 'workflow_status' }, { title: 'SLA giờ', dataIndex: 'due_hours' }, { title: 'Cảnh báo trước', dataIndex: 'warning_hours' }, { title: 'Mức', dataIndex: 'severity' }
      ]} />
    </Card>

    <Modal title="Thêm rủi ro" open={open} onCancel={() => setOpen(false)} onOk={submit} width={760}>
      <Form form={form} layout="vertical" initialValues={{ category: 'COMPLIANCE', likelihood: 3, impact: 3, status: 'OPEN' }}>
        <Row gutter={12}>
          <Col span={12}><Form.Item name="risk_code" label="Mã rủi ro" rules={[{ required: true }]}><Input placeholder="RR-2026-001" /></Form.Item></Col>
          <Col span={12}><Form.Item name="category" label="Nhóm"><Select options={['COMPLIANCE','TECHNICAL','PROCESS','PEOPLE','THIRD_PARTY'].map(x=>({value:x,label:x}))} /></Form.Item></Col>
        </Row>
        <Form.Item name="title" label="Tiêu đề" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        <Row gutter={12}>
          <Col span={8}><Form.Item name="profile_id" label="Hồ sơ"><Select allowClear options={profiles.map(p=>({value:p.id,label:p.profile_code}))} /></Form.Item></Col>
          <Col span={8}><Form.Item name="likelihood" label="Khả năng"><InputNumber min={1} max={5} style={{width:'100%'}} /></Form.Item></Col>
          <Col span={8}><Form.Item name="impact" label="Tác động"><InputNumber min={1} max={5} style={{width:'100%'}} /></Form.Item></Col>
        </Row>
        <Form.Item name="owner" label="Người phụ trách"><Input /></Form.Item>
        <Form.Item name="mitigation_plan" label="Phương án xử lý"><Input.TextArea rows={3} /></Form.Item>
      </Form>
    </Modal>
  </>;
}
