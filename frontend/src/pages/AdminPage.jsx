import React, { useEffect, useMemo, useState } from 'react';
import { Button, Card, Col, Form, Input, Modal, Popconfirm, Row, Select, Space, Switch, Table, Tabs, Tag, Tree, message } from 'antd';
import { ApartmentOutlined, LockOutlined, PlusOutlined, ReloadOutlined, TeamOutlined, UnlockOutlined, UserOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import StatusTag from '../components/StatusTag';
import { api } from '../api/client';

const defaultUserPassword = 'Admin@123';

function itemsOf(page) { return Array.isArray(page?.items) ? page.items : Array.isArray(page) ? page : []; }
function roleLabel(roleId, roles) { return roles.find((r) => r.id === roleId)?.code || roleId || ''; }
function orgLabel(orgId, orgs) { return orgs.find((o) => o.id === orgId)?.name || orgId || ''; }

function orgTreeData(nodes = []) {
  return nodes.map((n) => ({
    title: `${n.code} - ${n.name}`,
    key: n.id,
    children: orgTreeData(n.children || []),
  }));
}

export default function AdminPage() {
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [orgs, setOrgs] = useState([]);
  const [tree, setTree] = useState([]);
  const [idp, setIdp] = useState({});
  const [sec, setSec] = useState({});
  const [runtime, setRuntime] = useState({});
  const [prod, setProd] = useState({});

  const [userModal, setUserModal] = useState({ open: false, record: null });
  const [orgModal, setOrgModal] = useState({ open: false, record: null });
  const [roleModal, setRoleModal] = useState({ open: false, record: null });
  const [pwdModal, setPwdModal] = useState({ open: false, record: null });
  const [form] = Form.useForm();
  const [orgForm] = Form.useForm();
  const [roleForm] = Form.useForm();
  const [pwdForm] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const calls = await Promise.allSettled([
        api.users({ limit: 200 }),
        api.organizations({ limit: 200 }),
        api.organizationTree(),
        api.roles({ limit: 200 }),
        api.identityProviderStatus(),
        api.securitySummary(),
        api.runtime(),
        api.productionChecklist(),
      ]);
      const val = (i, d) => (calls[i].status === 'fulfilled' ? calls[i].value : d);
      setUsers(itemsOf(val(0, [])));
      setOrgs(itemsOf(val(1, [])));
      setTree(val(2, []));
      setRoles(itemsOf(val(3, [])));
      setIdp(val(4, {}));
      setSec(val(5, {}));
      setRuntime(val(6, {}));
      setProd(val(7, {}));
    } catch (e) {
      message.error(e.message || 'Không tải được dữ liệu quản trị');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const roleOptions = roles.map((r) => ({ value: r.id, label: `${r.code} - ${r.name}` }));
  const orgOptions = orgs.map((o) => ({ value: o.id, label: `${o.code} - ${o.name}` }));

  const openUser = (record = null) => {
    setUserModal({ open: true, record });
    form.resetFields();
    form.setFieldsValue(record ? { ...record, password: undefined } : { is_active: true, auth_provider: 'LOCAL', is_local_auth_allowed: true, password: defaultUserPassword });
  };
  const saveUser = async () => {
    const values = await form.validateFields();
    if (userModal.record) {
      const payload = { ...values };
      if (!payload.password) delete payload.password;
      await api.updateUser(userModal.record.id, payload);
      message.success('Đã cập nhật người dùng');
    } else {
      await api.createUser(values);
      message.success('Đã tạo người dùng');
    }
    setUserModal({ open: false, record: null });
    load();
  };

  const openOrg = (record = null) => {
    setOrgModal({ open: true, record });
    orgForm.resetFields();
    orgForm.setFieldsValue(record ? { ...record } : { is_active: true, org_type: 'department' });
  };
  const saveOrg = async () => {
    const values = await orgForm.validateFields();
    if (orgModal.record) {
      await api.updateOrganization(orgModal.record.id, values);
      message.success('Đã cập nhật đơn vị');
    } else {
      await api.createOrganization(values);
      message.success('Đã tạo đơn vị');
    }
    setOrgModal({ open: false, record: null });
    load();
  };

  const openRole = (record = null) => {
    setRoleModal({ open: true, record });
    roleForm.resetFields();
    roleForm.setFieldsValue(record ? { ...record } : {});
  };
  const saveRole = async () => {
    const values = await roleForm.validateFields();
    if (roleModal.record) {
      await api.updateRole(roleModal.record.id, values);
      message.success('Đã cập nhật vai trò');
    } else {
      await api.createRole(values);
      message.success('Đã tạo vai trò');
    }
    setRoleModal({ open: false, record: null });
    load();
  };

  const resetPassword = async () => {
    const values = await pwdForm.validateFields();
    await api.resetUserPassword(pwdModal.record.id, values);
    message.success('Đã đặt lại mật khẩu');
    setPwdModal({ open: false, record: null });
    load();
  };

  const userColumns = useMemo(() => [
    { title: 'Username', dataIndex: 'username' },
    { title: 'Họ tên', dataIndex: 'full_name' },
    { title: 'Email', dataIndex: 'email' },
    { title: 'Vai trò', dataIndex: 'role_id', render: (v) => <Tag>{roleLabel(v, roles)}</Tag> },
    { title: 'Đơn vị', dataIndex: 'organization_id', render: (v) => orgLabel(v, orgs) },
    { title: 'Trạng thái', dataIndex: 'is_active', render: (v) => <StatusTag value={v ? 'active' : 'inactive'} /> },
    { title: 'Auth', dataIndex: 'auth_provider' },
    { title: 'Thao tác', render: (_, r) => <Space wrap>
      <Button size="small" onClick={() => openUser(r)}>Sửa</Button>
      <Button size="small" onClick={() => { setPwdModal({ open: true, record: r }); pwdForm.setFieldsValue({ new_password: defaultUserPassword, must_change_password: true }); }}>Reset mật khẩu</Button>
      {r.is_active ? <Button size="small" icon={<LockOutlined />} onClick={async () => { await api.lockUser(r.id); message.success('Đã khóa'); load(); }}>Khóa</Button> : <Button size="small" icon={<UnlockOutlined />} onClick={async () => { await api.unlockUser(r.id); message.success('Đã mở khóa'); load(); }}>Mở khóa</Button>}
      <Popconfirm title="Xóa người dùng?" onConfirm={async () => { await api.deleteUser(r.id); message.success('Đã xóa'); load(); }}><Button size="small" danger disabled={r.username === 'admin'}>Xóa</Button></Popconfirm>
    </Space> },
  ], [roles, orgs]);

  const orgColumns = [
    { title: 'Code', dataIndex: 'code' },
    { title: 'Tên đơn vị', dataIndex: 'name' },
    { title: 'Loại', dataIndex: 'org_type' },
    { title: 'Cấp', dataIndex: 'level' },
    { title: 'Active', dataIndex: 'is_active', render: (v) => <StatusTag value={v ? 'active' : 'inactive'} /> },
    { title: 'Thao tác', render: (_, r) => <Space>
      <Button size="small" onClick={() => openOrg(r)}>Sửa</Button>
      <Popconfirm title="Xóa đơn vị?" onConfirm={async () => { await api.deleteOrganization(r.id); message.success('Đã xóa'); load(); }}><Button size="small" danger>Xóa</Button></Popconfirm>
    </Space> },
  ];

  const roleColumns = [
    { title: 'Code', dataIndex: 'code' },
    { title: 'Tên vai trò', dataIndex: 'name' },
    { title: 'Mô tả', dataIndex: 'description' },
    { title: 'Thao tác', render: (_, r) => <Space>
      <Button size="small" onClick={() => openRole(r)}>Sửa</Button>
      <Popconfirm title="Xóa vai trò?" onConfirm={async () => { await api.deleteRole(r.id); message.success('Đã xóa'); load(); }}><Button size="small" danger disabled={r.code === 'ADMIN'}>Xóa</Button></Popconfirm>
    </Space> },
  ];

  return <>
    <PageHeader title="Administration Center" subtitle="Quản lý người dùng, vai trò, đơn vị tổ chức và cấu hình nền tảng phục vụ UAT." />
    <Space style={{ marginBottom: 16 }}>
      <Button icon={<ReloadOutlined />} onClick={load}>Tải lại</Button>
    </Space>
    <Tabs items={[
      { key: 'users', label: 'Người dùng', children: <Card title="Người dùng" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => openUser()}>Thêm user</Button>}><Table loading={loading} rowKey="id" dataSource={users} columns={userColumns} scroll={{ x: 1100 }} /></Card> },
      { key: 'orgs', label: 'Đơn vị tổ chức', children: <Row gutter={[16,16]}><Col span={8}><Card title="Cây tổ chức"><Tree defaultExpandAll treeData={orgTreeData(tree)} /></Card></Col><Col span={16}><Card title="Danh sách đơn vị" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => openOrg()}>Thêm đơn vị</Button>}><Table loading={loading} rowKey="id" dataSource={orgs} columns={orgColumns} /></Card></Col></Row> },
      { key: 'roles', label: 'Vai trò', children: <Card title="Vai trò" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => openRole()}>Thêm vai trò</Button>}><Table loading={loading} rowKey="id" dataSource={roles} columns={roleColumns} /></Card> },
      { key: 'status', label: 'Trạng thái hệ thống', children: <Row gutter={[16,16]}><Col span={12}><JsonView title="Identity Provider" data={idp}/></Col><Col span={12}><JsonView title="Security Summary" data={sec}/></Col><Col span={12}><JsonView title="Runtime" data={runtime}/></Col><Col span={12}><JsonView title="Production Checklist" data={prod}/></Col></Row> },
    ]} />

    <Modal title={userModal.record ? 'Sửa người dùng' : 'Thêm người dùng'} open={userModal.open} onCancel={() => setUserModal({ open: false, record: null })} onOk={saveUser} width={720}>
      <Form form={form} layout="vertical">
        <Row gutter={12}><Col span={12}><Form.Item name="username" label="Username" rules={[{ required: true }]}><Input prefix={<UserOutlined />} disabled={!!userModal.record} /></Form.Item></Col><Col span={12}><Form.Item name="full_name" label="Họ tên" rules={[{ required: true }]}><Input /></Form.Item></Col></Row>
        <Row gutter={12}><Col span={12}><Form.Item name="email" label="Email"><Input /></Form.Item></Col><Col span={12}><Form.Item name="password" label={userModal.record ? 'Mật khẩu mới nếu cần đổi' : 'Mật khẩu'} rules={userModal.record ? [] : [{ required: true }]}><Input.Password /></Form.Item></Col></Row>
        <Row gutter={12}><Col span={12}><Form.Item name="role_id" label="Vai trò"><Select allowClear options={roleOptions} /></Form.Item></Col><Col span={12}><Form.Item name="organization_id" label="Đơn vị"><Select allowClear showSearch optionFilterProp="label" options={orgOptions} /></Form.Item></Col></Row>
        <Row gutter={12}><Col span={8}><Form.Item name="auth_provider" label="Auth Provider"><Select options={[{value:'LOCAL',label:'LOCAL'},{value:'LDAP',label:'LDAP'},{value:'SSO',label:'SSO'}]} /></Form.Item></Col><Col span={8}><Form.Item name="is_active" label="Active" valuePropName="checked"><Switch /></Form.Item></Col><Col span={8}><Form.Item name="is_local_auth_allowed" label="Cho phép login local" valuePropName="checked"><Switch /></Form.Item></Col></Row>
      </Form>
    </Modal>

    <Modal title={orgModal.record ? 'Sửa đơn vị' : 'Thêm đơn vị'} open={orgModal.open} onCancel={() => setOrgModal({ open: false, record: null })} onOk={saveOrg} width={720}>
      <Form form={orgForm} layout="vertical">
        <Row gutter={12}><Col span={8}><Form.Item name="code" label="Mã đơn vị" rules={[{ required: true }]}><Input prefix={<ApartmentOutlined />} /></Form.Item></Col><Col span={16}><Form.Item name="name" label="Tên đơn vị" rules={[{ required: true }]}><Input /></Form.Item></Col></Row>
        <Row gutter={12}><Col span={12}><Form.Item name="org_type" label="Loại đơn vị"><Select options={[{value:'head_office',label:'Hội sở'},{value:'center',label:'Trung tâm'},{value:'department',label:'Phòng ban'},{value:'business_unit',label:'Đơn vị nghiệp vụ'},{value:'branch',label:'Chi nhánh'}]} /></Form.Item></Col><Col span={12}><Form.Item name="parent_id" label="Đơn vị cha"><Select allowClear showSearch optionFilterProp="label" options={orgOptions} /></Form.Item></Col></Row>
        <Row gutter={12}><Col span={12}><Form.Item name="manager_name" label="Người phụ trách"><Input /></Form.Item></Col><Col span={12}><Form.Item name="contact_email" label="Email liên hệ"><Input /></Form.Item></Col></Row>
        <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="is_active" label="Active" valuePropName="checked"><Switch /></Form.Item>
      </Form>
    </Modal>

    <Modal title={roleModal.record ? 'Sửa vai trò' : 'Thêm vai trò'} open={roleModal.open} onCancel={() => setRoleModal({ open: false, record: null })} onOk={saveRole}>
      <Form form={roleForm} layout="vertical">
        <Form.Item name="code" label="Mã vai trò" rules={[{ required: true }]}><Input prefix={<TeamOutlined />} /></Form.Item>
        <Form.Item name="name" label="Tên vai trò" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
      </Form>
    </Modal>

    <Modal title={`Reset mật khẩu: ${pwdModal.record?.username || ''}`} open={pwdModal.open} onCancel={() => setPwdModal({ open: false, record: null })} onOk={resetPassword}>
      <Form form={pwdForm} layout="vertical">
        <Form.Item name="new_password" label="Mật khẩu mới" rules={[{ required: true }]}><Input.Password /></Form.Item>
        <Form.Item name="must_change_password" label="Bắt buộc đổi mật khẩu khi đăng nhập" valuePropName="checked"><Switch /></Form.Item>
      </Form>
    </Modal>
  </>;
}
