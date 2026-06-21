import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Col, Divider, Form, Input, InputNumber, Modal, Popconfirm, Row, Select, Space, Statistic, Table, Tabs, Tag, Typography, message } from 'antd';
import { DeleteOutlined, EditOutlined, ImportOutlined, PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

function items(x) { return Array.isArray(x?.items) ? x.items : []; }

const assetTypes = ['SERVER', 'STORAGE', 'SECURITY', 'NETWORK', 'VIRTUAL_MACHINE'];
const environments = ['PRODUCTION', 'DR', 'TEST', 'UAT'];
const criticalities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const statuses = ['ACTIVE', 'INACTIVE', 'RETIRED'];
const dbClasses = ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'SECRET'];
const deviceTypes = ['FIREWALL', 'SWITCH', 'ROUTER', 'WAF', 'IPS', 'LOAD_BALANCER'];
const yesNo = [{ value: false, label: 'Không' }, { value: true, label: 'Có' }];

function enumOptions(values) { return values.map(x => ({ value: x, label: x })); }
function cleanPayload(values) {
  const payload = { ...values };
  Object.keys(payload).forEach((k) => {
    if (payload[k] === '' || payload[k] === undefined) payload[k] = null;
  });
  return payload;
}

export default function CmdbPage({ profiles = [], systems = [] }) {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState({});
  const [assets, setAssets] = useState([]);
  const [applications, setApplications] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [devices, setDevices] = useState([]);
  const [inventory, setInventory] = useState(null);
  const [modal, setModal] = useState(null);
  const [importOpen, setImportOpen] = useState(false);
  const [importText, setImportText] = useState('[\n  {\n    "asset_code": "SRV-DEMO-01",\n    "asset_name": "Server Demo 01",\n    "asset_type": "SERVER",\n    "environment": "PRODUCTION",\n    "ip_address": "10.0.0.10",\n    "hostname": "srv-demo-01",\n    "criticality": "HIGH"\n  }\n]');
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const [s, a, apps, dbs, devs] = await Promise.all([
        api.cmdbDashboard(),
        api.cmdbAssets({ limit: 200 }),
        api.cmdbApplications({ limit: 200 }),
        api.cmdbDatabases({ limit: 200 }),
        api.cmdbNetworkDevices({ limit: 200 }),
      ]);
      setSummary(s);
      setAssets(items(a));
      setApplications(items(apps));
      setDatabases(items(dbs));
      setDevices(items(devs));
    } catch (e) {
      message.error(e.message);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { load(); }, []);

  const systemOptions = useMemo(() => systems.map(s => ({ value: s.id, label: `${s.code || s.id} - ${s.name}` })), [systems]);
  const profileOptions = useMemo(() => profiles.map(p => ({ value: p.id, label: `${p.profile_code || p.id} - cấp độ ${p.proposed_level}` })), [profiles]);

  const openCreate = (type) => {
    setModal({ type, mode: 'create', record: null });
    form.resetFields();
  };

  const openEdit = (type, record) => {
    setModal({ type, mode: 'edit', record });
    form.resetFields();
    form.setFieldsValue(record);
  };

  const save = async () => {
    const values = cleanPayload(await form.validateFields());
    const type = modal?.type;
    const isEdit = modal?.mode === 'edit';
    const id = modal?.record?.id;
    try {
      if (type === 'asset') {
        if (isEdit) await api.updateCmdbAsset(id, values); else await api.createCmdbAsset(values);
      }
      if (type === 'app') {
        if (isEdit) await api.updateCmdbApplication(id, values); else await api.createCmdbApplication(values);
      }
      if (type === 'db') {
        if (isEdit) await api.updateCmdbDatabase(id, values); else await api.createCmdbDatabase(values);
      }
      if (type === 'device') {
        if (isEdit) await api.updateCmdbNetworkDevice(id, values); else await api.createCmdbNetworkDevice(values);
      }
      message.success(isEdit ? 'Đã cập nhật dữ liệu CMDB' : 'Đã thêm dữ liệu CMDB');
      setModal(null);
      form.resetFields();
      load();
    } catch (e) {
      message.error(e.message);
    }
  };

  const remove = async (type, record) => {
    try {
      if (type === 'asset') await api.deleteCmdbAsset(record.id);
      if (type === 'app') await api.deleteCmdbApplication(record.id);
      if (type === 'db') await api.deleteCmdbDatabase(record.id);
      if (type === 'device') await api.deleteCmdbNetworkDevice(record.id);
      message.success('Đã xóa dữ liệu CMDB');
      load();
    } catch (e) {
      message.error(e.message);
    }
  };

  const importAssets = async () => {
    try {
      const parsed = JSON.parse(importText);
      if (!Array.isArray(parsed)) throw new Error('Dữ liệu import phải là mảng JSON');
      await api.cmdbImportAssets({ asset_type: 'SERVER', items: parsed });
      setImportOpen(false);
      message.success(`Đã import ${parsed.length} tài sản`);
      load();
    } catch (e) {
      message.error(e.message);
    }
  };

  const loadInventory = async (profileId) => {
    if (!profileId) return;
    try { setInventory(await api.cmdbProfileInventory(profileId)); } catch (e) { message.error(e.message); }
  };

  const syncProfile = async (profileId) => {
    if (!profileId) return;
    try {
      const r = await api.cmdbSyncProfile(profileId);
      setInventory(r);
      message.success('Đã đồng bộ CMDB vào hồ sơ');
    } catch (e) { message.error(e.message); }
  };

  const actionColumn = (type) => ({
    title: 'Thao tác',
    fixed: 'right',
    width: 150,
    render: (_, record) => <Space>
      <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(type, record)}>Sửa</Button>
      <Popconfirm title="Xóa dữ liệu CMDB này?" okText="Xóa" cancelText="Hủy" onConfirm={() => remove(type, record)}>
        <Button size="small" danger icon={<DeleteOutlined />}>Xóa</Button>
      </Popconfirm>
    </Space>,
  });

  const assetColumns = [
    { title: 'Mã', dataIndex: 'asset_code' },
    { title: 'Tên', dataIndex: 'asset_name' },
    { title: 'Loại', dataIndex: 'asset_type', render: v => <Tag>{v}</Tag> },
    { title: 'Môi trường', dataIndex: 'environment' },
    { title: 'IP', dataIndex: 'ip_address' },
    { title: 'Hostname', dataIndex: 'hostname' },
    { title: 'Criticality', dataIndex: 'criticality' },
    { title: 'Trạng thái', dataIndex: 'status' },
    actionColumn('asset'),
  ];
  const appColumns = [
    { title: 'Mã', dataIndex: 'app_code' },
    { title: 'Tên', dataIndex: 'app_name' },
    { title: 'Loại', dataIndex: 'app_type' },
    { title: 'Internet', dataIndex: 'internet_exposed', render: v => v ? <Tag color="red">Có</Tag> : <Tag>Không</Tag> },
    { title: 'API', dataIndex: 'has_api', render: v => v ? <Tag color="blue">Có</Tag> : <Tag>Không</Tag> },
    { title: 'Trạng thái', dataIndex: 'status' },
    actionColumn('app'),
  ];
  const dbColumns = [
    { title: 'Mã', dataIndex: 'db_code' },
    { title: 'Tên', dataIndex: 'db_name' },
    { title: 'Loại', dataIndex: 'db_type' },
    { title: 'Phân loại dữ liệu', dataIndex: 'data_classification' },
    { title: 'Dung lượng GB', dataIndex: 'size_gb' },
    { title: 'Dữ liệu nhạy cảm', render: (_, r) => (r.contains_personal_data || r.contains_financial_data) ? <Tag color="red">Có</Tag> : <Tag>Không</Tag> },
    { title: 'Trạng thái', dataIndex: 'status' },
    actionColumn('db'),
  ];
  const deviceColumns = [
    { title: 'Mã', dataIndex: 'device_code' },
    { title: 'Tên', dataIndex: 'device_name' },
    { title: 'Loại', dataIndex: 'device_type' },
    { title: 'Zone', dataIndex: 'zone' },
    { title: 'IP', dataIndex: 'ip_address' },
    { title: 'HA', dataIndex: 'ha_enabled', render: v => v ? <Tag color="green">Có</Tag> : <Tag>Không</Tag> },
    { title: 'Internet Edge', dataIndex: 'internet_edge', render: v => v ? <Tag color="red">Có</Tag> : <Tag>Không</Tag> },
    { title: 'Trạng thái', dataIndex: 'status' },
    actionColumn('device'),
  ];

  const tableProps = { loading, rowKey: 'id', scroll: { x: 1200 } };

  return <div>
    <PageHeader title="CMDB & Asset Inventory" subtitle="Quản lý tài sản CNTT, ứng dụng, CSDL, thiết bị mạng và đồng bộ dữ liệu vào hồ sơ đề xuất cấp độ" />
    <Alert
      showIcon
      type="info"
      message="Phân quyền CMDB"
      description="ADMIN và SECURITY_OFFICER được thêm/sửa/xóa/import dữ liệu CMDB. Các vai trò khác chỉ nên xem dữ liệu và sử dụng kết quả trong hồ sơ. Backend vẫn kiểm soát quyền khi gọi API."
      style={{ marginBottom: 16 }}
    />
    <Row gutter={16}>
      <Col span={4}><Card><Statistic title="Tài sản" value={summary.total_assets || 0} /></Card></Col>
      <Col span={4}><Card><Statistic title="Ứng dụng" value={summary.total_applications || 0} /></Card></Col>
      <Col span={4}><Card><Statistic title="CSDL" value={summary.total_databases || 0} /></Card></Col>
      <Col span={4}><Card><Statistic title="Thiết bị mạng" value={summary.total_network_devices || 0} /></Card></Col>
      <Col span={4}><Card><Statistic title="Chưa mapping" value={summary.unmapped_assets || 0} /></Card></Col>
      <Col span={4}><Card><Statistic title="DB nhạy cảm" value={summary.sensitive_databases || 0} /></Card></Col>
    </Row>
    <Card style={{ marginTop: 16 }}>
      <Space wrap>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openCreate('asset')}>Thêm tài sản</Button>
        <Button icon={<PlusOutlined />} onClick={() => openCreate('app')}>Thêm ứng dụng</Button>
        <Button icon={<PlusOutlined />} onClick={() => openCreate('db')}>Thêm CSDL</Button>
        <Button icon={<PlusOutlined />} onClick={() => openCreate('device')}>Thêm thiết bị mạng</Button>
        <Button icon={<ImportOutlined />} onClick={() => setImportOpen(true)}>Import tài sản JSON</Button>
        <Button icon={<ReloadOutlined />} onClick={load}>Tải lại</Button>
      </Space>
    </Card>
    <Tabs style={{ marginTop: 16 }} items={[
      { key: 'assets', label: 'Tài sản', children: <Table {...tableProps} columns={assetColumns} dataSource={assets} /> },
      { key: 'apps', label: 'Ứng dụng', children: <Table {...tableProps} columns={appColumns} dataSource={applications} /> },
      { key: 'dbs', label: 'CSDL', children: <Table {...tableProps} columns={dbColumns} dataSource={databases} /> },
      { key: 'devices', label: 'Thiết bị mạng', children: <Table {...tableProps} columns={deviceColumns} dataSource={devices} /> },
      { key: 'sync', label: 'Đồng bộ hồ sơ', children: <Card>
          <Alert
            showIcon
            type="warning"
            message="Đồng bộ CMDB vào hồ sơ"
            description="Chọn một hồ sơ cấp độ, hệ thống sẽ lấy các tài sản/ứng dụng/CSDL/thiết bị mạng đang gắn với hệ thống thông tin của hồ sơ đó và sinh lại phần mô tả phạm vi, kiến trúc kỹ thuật, inventory và cảnh báo thiếu dữ liệu. Chức năng này không xóa checklist hoặc minh chứng đã nhập."
            style={{ marginBottom: 16 }}
          />
          <Space wrap>
            <Select style={{ width: 420 }} placeholder="Chọn hồ sơ" options={profileOptions} onChange={loadInventory} />
            <Button type="primary" onClick={() => inventory?.profile_id && syncProfile(inventory.profile_id)}>Đồng bộ CMDB vào hồ sơ</Button>
          </Space>
          <Divider />
          {inventory?.warnings?.length ? <Alert type="warning" showIcon message="Cảnh báo hồ sơ" description={<ul>{inventory.warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>} /> : null}
          {inventory ? <JsonView data={inventory} /> : <Typography.Text type="secondary">Chọn hồ sơ để xem inventory.</Typography.Text>}
        </Card> },
    ]} />

    <Modal open={!!modal} title={modal?.mode === 'edit' ? 'Sửa dữ liệu CMDB' : 'Thêm dữ liệu CMDB'} onOk={save} onCancel={() => setModal(null)} width={760} destroyOnClose>
      <Form form={form} layout="vertical">
        {modal?.type === 'asset' && <>
          <Form.Item name="asset_code" label="Mã tài sản" rules={[{ required: modal?.mode !== 'edit' }]}><Input disabled={modal?.mode === 'edit'} /></Form.Item>
          <Form.Item name="asset_name" label="Tên tài sản" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="asset_type" label="Loại" initialValue="SERVER"><Select options={enumOptions(assetTypes)} /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="environment" label="Môi trường"><Select allowClear options={enumOptions(environments)} /></Form.Item>
          <Form.Item name="ip_address" label="IP"><Input /></Form.Item>
          <Form.Item name="hostname" label="Hostname"><Input /></Form.Item>
          <Form.Item name="operating_system" label="Hệ điều hành"><Input /></Form.Item>
          <Form.Item name="criticality" label="Mức độ quan trọng" initialValue="MEDIUM"><Select options={enumOptions(criticalities)} /></Form.Item>
          <Form.Item name="status" label="Trạng thái" initialValue="ACTIVE"><Select options={enumOptions(statuses)} /></Form.Item>
          <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        </>}
        {modal?.type === 'app' && <>
          <Form.Item name="app_code" label="Mã ứng dụng" rules={[{ required: modal?.mode !== 'edit' }]}><Input disabled={modal?.mode === 'edit'} /></Form.Item>
          <Form.Item name="app_name" label="Tên ứng dụng" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="app_type" label="Loại" initialValue="BUSINESS"><Input /></Form.Item>
          <Form.Item name="technology_stack" label="Công nghệ"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item name="internet_exposed" label="Internet exposed" initialValue={false}><Select options={yesNo} /></Form.Item>
          <Form.Item name="has_api" label="Có API" initialValue={false}><Select options={yesNo} /></Form.Item>
          <Form.Item name="status" label="Trạng thái" initialValue="ACTIVE"><Select options={enumOptions(statuses)} /></Form.Item>
          <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        </>}
        {modal?.type === 'db' && <>
          <Form.Item name="db_code" label="Mã CSDL" rules={[{ required: modal?.mode !== 'edit' }]}><Input disabled={modal?.mode === 'edit'} /></Form.Item>
          <Form.Item name="db_name" label="Tên CSDL" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="db_type" label="Loại CSDL" initialValue="ORACLE"><Input /></Form.Item>
          <Form.Item name="data_classification" label="Phân loại dữ liệu" initialValue="INTERNAL"><Select options={enumOptions(dbClasses)} /></Form.Item>
          <Form.Item name="contains_personal_data" label="Dữ liệu cá nhân" initialValue={false}><Select options={yesNo} /></Form.Item>
          <Form.Item name="contains_financial_data" label="Dữ liệu tài chính" initialValue={false}><Select options={yesNo} /></Form.Item>
          <Form.Item name="size_gb" label="Dung lượng GB"><InputNumber min={0} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="status" label="Trạng thái" initialValue="ACTIVE"><Select options={enumOptions(statuses)} /></Form.Item>
          <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        </>}
        {modal?.type === 'device' && <>
          <Form.Item name="device_code" label="Mã thiết bị" rules={[{ required: modal?.mode !== 'edit' }]}><Input disabled={modal?.mode === 'edit'} /></Form.Item>
          <Form.Item name="device_name" label="Tên thiết bị" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="device_type" label="Loại" initialValue="FIREWALL"><Select options={enumOptions(deviceTypes)} /></Form.Item>
          <Form.Item name="zone" label="Zone"><Input /></Form.Item>
          <Form.Item name="ip_address" label="IP"><Input /></Form.Item>
          <Form.Item name="ha_enabled" label="HA" initialValue={false}><Select options={yesNo} /></Form.Item>
          <Form.Item name="internet_edge" label="Internet Edge" initialValue={false}><Select options={yesNo} /></Form.Item>
          <Form.Item name="status" label="Trạng thái" initialValue="ACTIVE"><Select options={enumOptions(statuses)} /></Form.Item>
          <Form.Item name="description" label="Mô tả"><Input.TextArea rows={3} /></Form.Item>
        </>}
      </Form>
    </Modal>

    <Modal open={importOpen} title="Import tài sản CMDB bằng JSON" onOk={importAssets} onCancel={() => setImportOpen(false)} width={820} okText="Import">
      <Alert
        showIcon
        type="info"
        message="Định dạng import"
        description="Nhập một mảng JSON. Mỗi phần tử là một tài sản CMDB với các trường như asset_code, asset_name, asset_type, environment, ip_address, hostname, criticality, information_system_id."
        style={{ marginBottom: 12 }}
      />
      <Input.TextArea rows={14} value={importText} onChange={(e) => setImportText(e.target.value)} />
    </Modal>
  </div>;
}
