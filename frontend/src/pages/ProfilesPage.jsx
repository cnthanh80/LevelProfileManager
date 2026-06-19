import { Button, Drawer, Form, Input, InputNumber, Modal, Select, Space, Tabs, message } from 'antd';
import { useState } from 'react';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import StatusTag from '../components/StatusTag';
import ProfileDetail from './ProfileDetail';
import { api } from '../api/client';

export default function ProfilesPage({ items, systems, reload }) {
  const [open, setOpen] = useState(false); const [editing, setEditing] = useState(null); const [selected, setSelected] = useState(null); const [form] = Form.useForm();
  const startCreate = () => { setEditing(null); form.resetFields(); form.setFieldsValue({ status: 'DRAFT', proposed_level: 2, information_system_id: systems?.[0]?.id }); setOpen(true); };
  const startEdit = (r) => { setEditing(r); form.setFieldsValue(r); setOpen(true); };
  const submit = async () => { const values = await form.validateFields(); editing ? await api.updateProfile(editing.id, values) : await api.createProfile(values); message.success('Đã lưu hồ sơ'); setOpen(false); reload(); };
  const remove = (r) => Modal.confirm({ title: 'Xóa hồ sơ?', content: r.profile_code, onOk: async () => { await api.deleteProfile(r.id); message.success('Đã xóa'); reload(); } });
  return <>
    <PageHeader title="Hồ sơ đề xuất cấp độ" subtitle="Quản lý vòng đời hồ sơ: tạo, checklist, minh chứng, workflow, xuất tài liệu." actions={<Button type="primary" onClick={startCreate}>Tạo hồ sơ</Button>} />
    <DataTable data={items} columns={[
      { title: 'Mã hồ sơ', dataIndex: 'profile_code', fixed: 'left' }, { title: 'HTTT ID', dataIndex: 'information_system_id' },
      { title: 'Cấp độ', dataIndex: 'proposed_level', render: (v) => `Cấp ${v}` }, { title: 'Trạng thái', dataIndex: 'status', render: (v) => <StatusTag value={v} /> },
      { title: 'Thao tác', width: 280, render: (_, r) => <Space><Button type="primary" onClick={() => setSelected(r)}>Mở hồ sơ</Button><Button onClick={() => startEdit(r)}>Sửa</Button><Button danger onClick={() => remove(r)}>Xóa</Button></Space> }
    ]} />
    <Drawer title={editing ? 'Cập nhật hồ sơ' : 'Tạo hồ sơ'} open={open} onClose={() => setOpen(false)} width={760} extra={<Button type="primary" onClick={submit}>Lưu</Button>}>
      <Form form={form} layout="vertical">
        <Form.Item name="profile_code" label="Mã hồ sơ" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="information_system_id" label="Hệ thống thông tin" rules={[{ required: true }]}><Select options={(systems||[]).map(s => ({ value: s.id, label: `${s.code} - ${s.name}` }))} /></Form.Item>
        <Form.Item name="proposed_level" label="Cấp độ đề xuất"><InputNumber min={1} max={5} style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="status" label="Trạng thái"><Input /></Form.Item>
        <Form.Item name="basis_for_level" label="Căn cứ xác định cấp độ"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="system_scope_description" label="Thuyết minh phạm vi"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="technical_architecture" label="Kiến trúc kỹ thuật"><Input.TextArea rows={3} /></Form.Item>
        <Tabs items={['confidentiality_impact','integrity_impact','availability_impact'].map(k => ({ key:k, label:k, children:<Form.Item name={k}><Input.TextArea rows={3} /></Form.Item> }))} />
      </Form>
    </Drawer>
    <Drawer title={`Chi tiết hồ sơ ${selected?.profile_code || ''}`} open={!!selected} onClose={() => setSelected(null)} width="90%" destroyOnClose>
      {selected && <ProfileDetail profile={selected} reload={reload} />}
    </Drawer>
  </>;
}
