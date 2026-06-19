import { Button, Card, Col, Form, Input, Modal, Row, Select, Space, Statistic, Switch, Table, Tree, Typography, message } from 'antd';
import React, { useEffect, useMemo, useState } from 'react';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

function flattenTree(nodes, rows = []) {
  for (const node of nodes || []) {
    rows.push(node);
    flattenTree(node.children || [], rows);
  }
  return rows;
}

function toTreeData(nodes) {
  return (nodes || []).map((n) => ({
    key: String(n.id),
    title: `${n.code} - ${n.name}`,
    children: toTreeData(n.children || []),
  }));
}

export default function OrganizationsPage() {
  const [tree, setTree] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const flat = useMemo(() => flattenTree(tree, []), [tree]);
  const options = flat.map((o) => ({ value: o.id, label: `${o.code} - ${o.name}` }));

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.organizationTree();
      setTree(data || []);
      const first = flattenTree(data || [])[0];
      if (first) setSummary(await api.organizationScopeSummary(first.id));
    } catch (e) { message.error(e.message || 'Không tải được cây tổ chức'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const onSelect = async (keys) => {
    if (!keys?.length) return;
    try { setSummary(await api.organizationScopeSummary(keys[0])); }
    catch (e) { message.error(e.message || 'Không tải được thống kê đơn vị'); }
  };

  const create = async () => {
    const values = await form.validateFields();
    await api.createOrganization(values);
    setOpen(false); form.resetFields(); message.success('Đã tạo đơn vị'); load();
  };

  return <>
    <PageHeader title="Quản lý nhiều đơn vị" subtitle="Cây tổ chức, phạm vi dữ liệu và thống kê hồ sơ theo đơn vị." extra={<Space><Button icon={<ReloadOutlined />} onClick={load}>Tải lại</Button><Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>Thêm đơn vị</Button></Space>} />
    <Row gutter={[16,16]}>
      <Col xs={24} lg={8}>
        <Card title="Cây tổ chức" loading={loading}>
          <Tree defaultExpandAll treeData={toTreeData(tree)} onSelect={onSelect} />
        </Card>
      </Col>
      <Col xs={24} lg={16}>
        <Row gutter={[16,16]}>
          <Col span={8}><Card><Statistic title="Người dùng" value={summary?.users_count || 0} /></Card></Col>
          <Col span={8}><Card><Statistic title="Hệ thống" value={summary?.systems_count || 0} /></Card></Col>
          <Col span={8}><Card><Statistic title="Hồ sơ" value={summary?.profiles_count || 0} /></Card></Col>
        </Row>
        <Row gutter={[16,16]} style={{ marginTop: 16 }}>
          <Col span={6}><Card><Statistic title="Cấp độ 2" value={summary?.level_2_systems || 0} /></Card></Col>
          <Col span={6}><Card><Statistic title="Cấp độ 3" value={summary?.level_3_systems || 0} /></Card></Col>
          <Col span={6}><Card><Statistic title="Cấp độ 4" value={summary?.level_4_systems || 0} /></Card></Col>
          <Col span={6}><Card><Statistic title="Cấp độ 5" value={summary?.level_5_systems || 0} /></Card></Col>
        </Row>
        <JsonView title="Phạm vi đơn vị đang chọn" data={summary || {}} />
      </Col>
    </Row>
    <Card title="Danh sách đơn vị" style={{ marginTop: 16 }}>
      <Table rowKey="id" dataSource={flat} loading={loading} columns={[
        { title: 'Mã', dataIndex: 'code' },
        { title: 'Tên đơn vị', dataIndex: 'name' },
        { title: 'Loại', dataIndex: 'org_type' },
        { title: 'Cấp cây', dataIndex: 'level' },
        { title: 'Đường dẫn', dataIndex: 'path' },
        { title: 'Người phụ trách', dataIndex: 'manager_name' },
        { title: 'Active', dataIndex: 'is_active', render: (v) => v ? 'Có' : 'Không' },
      ]} />
    </Card>
    <Modal title="Thêm đơn vị" open={open} onOk={create} onCancel={() => setOpen(false)} okText="Lưu" cancelText="Hủy">
      <Form layout="vertical" form={form} initialValues={{ is_active: true, org_type: 'department' }}>
        <Form.Item name="code" label="Mã đơn vị" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="name" label="Tên đơn vị" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="parent_id" label="Đơn vị cha"><Select allowClear options={options} /></Form.Item>
        <Form.Item name="org_type" label="Loại đơn vị"><Select options={[{value:'head_office',label:'Hội sở'}, {value:'internal_unit',label:'Đơn vị nội bộ'}, {value:'department',label:'Phòng/Ban'}, {value:'branch',label:'Chi nhánh'}, {value:'business_unit',label:'Đơn vị nghiệp vụ'}]} /></Form.Item>
        <Form.Item name="manager_name" label="Người phụ trách"><Input /></Form.Item>
        <Form.Item name="contact_email" label="Email liên hệ"><Input /></Form.Item>
        <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="is_active" label="Hoạt động" valuePropName="checked"><Switch /></Form.Item>
      </Form>
    </Modal>
  </>;
}
