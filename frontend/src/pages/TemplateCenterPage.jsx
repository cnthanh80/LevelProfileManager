import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Drawer, Form, Input, InputNumber, Modal, Row, Select, Space, Statistic, Table, Tag, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import StatusTag from '../components/StatusTag';
import { api, downloadUrl } from '../api/client';

function pickItems(x) { return Array.isArray(x?.items) ? x.items : Array.isArray(x) ? x : []; }

export default function TemplateCenterPage({ profiles = [] }) {
  const [items, setItems] = useState([]);
  const [types, setTypes] = useState([]);
  const [summary, setSummary] = useState({});
  const [variables, setVariables] = useState({});
  const [preview, setPreview] = useState(null);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form] = Form.useForm();

  const load = async () => {
    const [t, s, ty, v] = await Promise.allSettled([
      api.documentTemplates({ limit: 200, active_only: false }), api.templateCenterSummary(), api.governmentDocumentTypes(), api.templateVariables()
    ]);
    if (t.status === 'fulfilled') setItems(pickItems(t.value));
    if (s.status === 'fulfilled') setSummary(s.value || {});
    if (ty.status === 'fulfilled') setTypes(Array.isArray(ty.value) ? ty.value : []);
    if (v.status === 'fulfilled') setVariables(v.value || {});
  };
  useEffect(() => { load(); }, []);

  const startCreate = () => {
    setEditing(null); form.resetFields();
    form.setFieldsValue({ document_type: 'PROFILE_EXPLANATION', category: 'GOVERNMENT', version: '1.0', file_format: 'docx', is_active: true, is_default: false, sort_order: 100 });
    setOpen(true);
  };
  const startEdit = (r) => { setEditing(r); form.setFieldsValue(r); setOpen(true); };
  const submit = async () => {
    const values = await form.validateFields();
    editing ? await api.updateDocumentTemplate(editing.id, values) : await api.createDocumentTemplate(values);
    message.success('Đã lưu biểu mẫu'); setOpen(false); load();
  };
  const uploadFile = async (tpl, file) => {
    const fd = new FormData(); fd.append('file', file);
    await api.uploadDocumentTemplate(tpl.id, fd); message.success('Đã upload file template'); load();
    return false;
  };
  const activate = async (r) => { await api.activateDocumentTemplate(r.id); message.success('Đã đặt làm mẫu mặc định'); load(); };
  const deactivate = async (r) => { await api.deactivateDocumentTemplate(r.id); message.success('Đã ngừng kích hoạt'); load(); };
  const previewContext = async (r) => {
    const profileId = profiles?.[0]?.id;
    if (!profileId) return message.warning('Chưa có hồ sơ để preview context');
    const res = await api.previewTemplateContext({ profile_id: profileId, template_code: r.code, document_type: r.document_type });
    setPreview(res);
  };

  return <>
    <PageHeader title="Kho biểu mẫu cơ quan" subtitle="Quản lý mẫu hồ sơ, tờ trình, công văn, quyết định và phụ lục checklist theo cơ quan/đơn vị." actions={<Button type="primary" onClick={startCreate}>Tạo biểu mẫu</Button>} />
    <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
      <Col xs={24} md={6}><Card><Statistic title="Tổng biểu mẫu" value={summary.total_templates || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Đang kích hoạt" value={summary.active_templates || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Có file upload" value={summary.uploaded_templates || 0} /></Card></Col>
      <Col xs={24} md={6}><Card><Statistic title="Mẫu mặc định" value={summary.default_templates || 0} /></Card></Col>
    </Row>
    <Card title="Danh sách biểu mẫu">
      <Table rowKey="id" dataSource={items} scroll={{ x: 1300 }} columns={[
        { title: 'Mã', dataIndex: 'code', fixed: 'left', width: 220 },
        { title: 'Tên biểu mẫu', dataIndex: 'name', width: 260 },
        { title: 'Loại văn bản', dataIndex: 'document_type', width: 220, render: v => <StatusTag value={v} /> },
        { title: 'Nhóm', dataIndex: 'category', width: 140, render: v => <Tag>{v}</Tag> },
        { title: 'Phiên bản', dataIndex: 'version', width: 100 },
        { title: 'Cơ quan', dataIndex: 'agency_name', width: 240 },
        { title: 'File', dataIndex: 'template_path', width: 120, render: (v, r) => v ? <a href={downloadUrl(`/document-templates/${r.id}/download`)} target="_blank" rel="noreferrer">Tải file</a> : '—' },
        { title: 'Trạng thái', dataIndex: 'is_active', width: 120, render: v => v ? <Tag color="green">Active</Tag> : <Tag>Inactive</Tag> },
        { title: 'Mặc định', dataIndex: 'is_default', width: 120, render: v => v ? <Tag color="blue">Default</Tag> : '—' },
        { title: 'Thao tác', fixed: 'right', width: 360, render: (_, r) => <Space wrap>
          <Button onClick={() => startEdit(r)}>Sửa</Button>
          <Upload showUploadList={false} beforeUpload={(file) => uploadFile(r, file)}><Button icon={<UploadOutlined />}>Upload</Button></Upload>
          <Button onClick={() => activate(r)}>Default</Button>
          <Button onClick={() => previewContext(r)}>Preview</Button>
          <Button danger onClick={() => Modal.confirm({ title: 'Ngừng kích hoạt biểu mẫu?', onOk: () => deactivate(r) })}>Off</Button>
        </Space> }
      ]} />
    </Card>
    <Row gutter={[16,16]} style={{ marginTop: 16 }}>
      <Col xs={24} md={12}><JsonView title="Biến template hỗ trợ" data={variables} /></Col>
      <Col xs={24} md={12}><JsonView title="Preview context" data={preview || { note: 'Chọn Preview trên một biểu mẫu để xem dữ liệu đổ mẫu.' }} /></Col>
    </Row>
    <Drawer title={editing ? 'Cập nhật biểu mẫu' : 'Tạo biểu mẫu'} open={open} onClose={() => setOpen(false)} width={760} extra={<Button type="primary" onClick={submit}>Lưu</Button>} destroyOnClose>
      <Form form={form} layout="vertical">
        <Form.Item name="code" label="Mã biểu mẫu" rules={[{ required: true }]}><Input disabled={!!editing} /></Form.Item>
        <Form.Item name="name" label="Tên biểu mẫu" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="document_type" label="Loại văn bản" rules={[{ required: true }]}><Select options={types.map(t => ({ value: t.code, label: `${t.code} - ${t.title}` }))} /></Form.Item>
        <Form.Item name="category" label="Nhóm"><Select options={[{value:'GOVERNMENT',label:'Văn bản nhà nước'}, {value:'INTERNAL',label:'Nội bộ'}, {value:'REPORT',label:'Báo cáo'}, {value:'CUSTOM',label:'Tùy biến'}]} /></Form.Item>
        <Form.Item name="version" label="Phiên bản"><Input /></Form.Item>
        <Form.Item name="agency_name" label="Tên cơ quan"><Input /></Form.Item>
        <Form.Item name="official_number_prefix" label="Tiền tố số/ký hiệu văn bản"><Input placeholder="VD: /NHCS-CNTT" /></Form.Item>
        <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="variable_schema" label="Ghi chú biến template"><Input.TextArea rows={4} /></Form.Item>
        <Form.Item name="sort_order" label="Thứ tự"><InputNumber min={1} max={9999} style={{ width: '100%' }} /></Form.Item>
      </Form>
    </Drawer>
  </>;
}
