import { Button, Drawer, Form, Input, InputNumber, Modal, Select, Space, message } from 'antd';
import React, { useState } from 'react';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import StatusTag from '../components/StatusTag';
import { api } from '../api/client';

export default function SystemsPage({ items, reload }) {
  const [open, setOpen] = useState(false); const [editing, setEditing] = useState(null); const [form] = Form.useForm();
  const startCreate = () => { setEditing(null); form.resetFields(); form.setFieldsValue({ operation_status: 'active', environment: 'production', deployment_model: 'on_premise' }); setOpen(true); };
  const startEdit = (r) => { setEditing(r); form.setFieldsValue(r); setOpen(true); };
  const submit = async () => { const values = await form.validateFields(); editing ? await api.updateSystem(editing.id, values) : await api.createSystem(values); message.success('Đã lưu hệ thống'); setOpen(false); reload(); };
  const remove = (r) => Modal.confirm({ title: 'Xóa hệ thống?', content: r.name, onOk: async () => { await api.deleteSystem(r.id); message.success('Đã xóa'); reload(); } });
  return <>
    <PageHeader title="Danh mục hệ thống thông tin" subtitle="Quản lý hệ thống nội bộ, chủ quản, vận hành, môi trường và cấp độ dự kiến." actions={<Button type="primary" onClick={startCreate}>Tạo hệ thống</Button>} />
    <DataTable data={items} columns={[
      { title: 'Mã', dataIndex: 'code', fixed: 'left' }, { title: 'Tên hệ thống', dataIndex: 'name' },
      { title: 'Cấp độ', dataIndex: 'proposed_level', render: (v) => v ? `Cấp ${v}` : '—' },
      { title: 'Triển khai', dataIndex: 'deployment_model', render: (v) => <StatusTag value={v} /> },
      { title: 'Môi trường', dataIndex: 'environment', render: (v) => <StatusTag value={v} /> },
      { title: 'Trạng thái', dataIndex: 'operation_status', render: (v) => <StatusTag value={v} /> },
      { title: 'Thao tác', render: (_, r) => <Space><Button onClick={() => startEdit(r)}>Sửa</Button><Button danger onClick={() => remove(r)}>Xóa</Button></Space> }
    ]} />
    <Drawer title={editing ? 'Cập nhật hệ thống' : 'Tạo hệ thống'} open={open} onClose={() => setOpen(false)} width={720} extra={<Button type="primary" onClick={submit}>Lưu</Button>}>
      <Form form={form} layout="vertical">
        <Form.Item name="code" label="Mã hệ thống" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="name" label="Tên hệ thống" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="proposed_level" label="Cấp độ dự kiến"><InputNumber min={1} max={5} style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="deployment_model" label="Mô hình triển khai"><Select options={[{value:'on_premise',label:'On-premise'},{value:'cloud',label:'Cloud'},{value:'hybrid',label:'Hybrid'}]} /></Form.Item>
        <Form.Item name="environment" label="Môi trường"><Select options={[{value:'production',label:'Production'},{value:'dr',label:'DR'},{value:'test',label:'Test'}]} /></Form.Item>
        <Form.Item name="operation_status" label="Trạng thái"><Select options={[{value:'active',label:'Active'},{value:'inactive',label:'Inactive'}]} /></Form.Item>
        <Form.Item name="purpose" label="Mục tiêu"><Input.TextArea rows={2} /></Form.Item>
        <Form.Item name="scope" label="Phạm vi"><Input.TextArea rows={2} /></Form.Item>
        <Form.Item name="main_functions" label="Chức năng chính"><Input.TextArea rows={2} /></Form.Item>
        <Form.Item name="data_types" label="Loại dữ liệu xử lý"><Input.TextArea rows={2} /></Form.Item>
      </Form>
    </Drawer>
  </>;
}
