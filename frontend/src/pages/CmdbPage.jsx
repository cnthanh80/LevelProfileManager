import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Col, Divider, Form, Input, InputNumber, Modal, Row, Select, Space, Statistic, Table, Tabs, Tag, Typography, message } from 'antd';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

function items(x) { return Array.isArray(x?.items) ? x.items : []; }

export default function CmdbPage({ profiles = [], systems = [] }) {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState({});
  const [assets, setAssets] = useState([]);
  const [applications, setApplications] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [devices, setDevices] = useState([]);
  const [inventory, setInventory] = useState(null);
  const [modal, setModal] = useState(null);
  const [form] = Form.useForm();

  const load = async () => {
    setLoading(true);
    try {
      const [s, a, apps, dbs, devs] = await Promise.all([
        api.cmdbDashboard(), api.cmdbAssets({ limit: 100 }), api.cmdbApplications({ limit: 100 }), api.cmdbDatabases({ limit: 100 }), api.cmdbNetworkDevices({ limit: 100 })
      ]);
      setSummary(s); setAssets(items(a)); setApplications(items(apps)); setDatabases(items(dbs)); setDevices(items(devs));
    } catch (e) { message.error(e.message); } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const systemOptions = systems.map(s => ({ value: s.id, label: `${s.code || s.id} - ${s.name}` }));
  const profileOptions = profiles.map(p => ({ value: p.id, label: `${p.profile_code || p.id} - cấp độ ${p.proposed_level}` }));

  const create = async () => {
    const values = await form.validateFields();
    try {
      if (modal === 'asset') await api.createCmdbAsset(values);
      if (modal === 'app') await api.createCmdbApplication(values);
      if (modal === 'db') await api.createCmdbDatabase(values);
      if (modal === 'device') await api.createCmdbNetworkDevice(values);
      message.success('Đã lưu dữ liệu CMDB'); setModal(null); form.resetFields(); load();
    } catch (e) { message.error(e.message); }
  };

  const loadInventory = async (profileId) => {
    if (!profileId) return;
    try { setInventory(await api.cmdbProfileInventory(profileId)); } catch (e) { message.error(e.message); }
  };
  const syncProfile = async (profileId) => {
    if (!profileId) return;
    try { const r = await api.cmdbSyncProfile(profileId); setInventory(r); message.success('Đã đồng bộ CMDB vào hồ sơ'); } catch (e) { message.error(e.message); }
  };

  const assetColumns = [
    { title: 'Mã', dataIndex: 'asset_code' }, { title: 'Tên', dataIndex: 'asset_name' }, { title: 'Loại', dataIndex: 'asset_type', render: v => <Tag>{v}</Tag> },
    { title: 'Môi trường', dataIndex: 'environment' }, { title: 'IP', dataIndex: 'ip_address' }, { title: 'Hostname', dataIndex: 'hostname' }, { title: 'Criticality', dataIndex: 'criticality' },
  ];
  const appColumns = [
    { title: 'Mã', dataIndex: 'app_code' }, { title: 'Tên', dataIndex: 'app_name' }, { title: 'Loại', dataIndex: 'app_type' },
    { title: 'Internet', dataIndex: 'internet_exposed', render: v => v ? <Tag color="red">Có</Tag> : <Tag>Không</Tag> },
    { title: 'API', dataIndex: 'has_api', render: v => v ? <Tag color="blue">Có</Tag> : <Tag>Không</Tag> },
  ];
  const dbColumns = [
    { title: 'Mã', dataIndex: 'db_code' }, { title: 'Tên', dataIndex: 'db_name' }, { title: 'Loại', dataIndex: 'db_type' }, { title: 'Phân loại dữ liệu', dataIndex: 'data_classification' },
    { title: 'Dữ liệu nhạy cảm', render: (_, r) => (r.contains_personal_data || r.contains_financial_data) ? <Tag color="red">Có</Tag> : <Tag>Không</Tag> },
  ];
  const deviceColumns = [
    { title: 'Mã', dataIndex: 'device_code' }, { title: 'Tên', dataIndex: 'device_name' }, { title: 'Loại', dataIndex: 'device_type' }, { title: 'Zone', dataIndex: 'zone' },
    { title: 'HA', dataIndex: 'ha_enabled', render: v => v ? <Tag color="green">Có</Tag> : <Tag>Không</Tag> },
    { title: 'Internet Edge', dataIndex: 'internet_edge', render: v => v ? <Tag color="red">Có</Tag> : <Tag>Không</Tag> },
  ];

  return <div>
    <PageHeader title="CMDB & Asset Inventory" subtitle="Quản lý tài sản CNTT và đồng bộ dữ liệu vào hồ sơ đề xuất cấp độ" />
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
        <Button type="primary" onClick={() => { setModal('asset'); form.resetFields(); }}>Thêm tài sản</Button>
        <Button onClick={() => { setModal('app'); form.resetFields(); }}>Thêm ứng dụng</Button>
        <Button onClick={() => { setModal('db'); form.resetFields(); }}>Thêm CSDL</Button>
        <Button onClick={() => { setModal('device'); form.resetFields(); }}>Thêm thiết bị mạng</Button>
        <Button onClick={load}>Tải lại</Button>
      </Space>
    </Card>
    <Tabs style={{ marginTop: 16 }} items={[
      { key: 'assets', label: 'Tài sản', children: <Table loading={loading} rowKey="id" columns={assetColumns} dataSource={assets} /> },
      { key: 'apps', label: 'Ứng dụng', children: <Table loading={loading} rowKey="id" columns={appColumns} dataSource={applications} /> },
      { key: 'dbs', label: 'CSDL', children: <Table loading={loading} rowKey="id" columns={dbColumns} dataSource={databases} /> },
      { key: 'devices', label: 'Thiết bị mạng', children: <Table loading={loading} rowKey="id" columns={deviceColumns} dataSource={devices} /> },
      { key: 'sync', label: 'Đồng bộ hồ sơ', children: <Card>
          <Space wrap>
            <Select style={{ width: 420 }} placeholder="Chọn hồ sơ" options={profileOptions} onChange={loadInventory} />
            <Button type="primary" onClick={() => inventory?.profile_id && syncProfile(inventory.profile_id)}>Đồng bộ CMDB vào hồ sơ</Button>
          </Space>
          <Divider />
          {inventory?.warnings?.length ? <Alert type="warning" showIcon message="Cảnh báo hồ sơ" description={<ul>{inventory.warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>} /> : null}
          {inventory ? <JsonView data={inventory} /> : <Typography.Text type="secondary">Chọn hồ sơ để xem inventory.</Typography.Text>}
        </Card> },
    ]} />
    <Modal open={!!modal} title="Thêm dữ liệu CMDB" onOk={create} onCancel={() => setModal(null)} width={720}>
      <Form form={form} layout="vertical">
        {modal === 'asset' && <>
          <Form.Item name="asset_code" label="Mã tài sản" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="asset_name" label="Tên tài sản" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="asset_type" label="Loại" initialValue="SERVER"><Select options={['SERVER','STORAGE','SECURITY','NETWORK','VIRTUAL_MACHINE'].map(x=>({value:x,label:x}))} /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="environment" label="Môi trường"><Select allowClear options={['PRODUCTION','DR','TEST','UAT'].map(x=>({value:x,label:x}))} /></Form.Item>
          <Form.Item name="ip_address" label="IP"><Input /></Form.Item><Form.Item name="hostname" label="Hostname"><Input /></Form.Item>
          <Form.Item name="criticality" label="Mức độ quan trọng" initialValue="MEDIUM"><Select options={['LOW','MEDIUM','HIGH','CRITICAL'].map(x=>({value:x,label:x}))} /></Form.Item>
        </>}
        {modal === 'app' && <>
          <Form.Item name="app_code" label="Mã ứng dụng" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="app_name" label="Tên ứng dụng" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="app_type" label="Loại" initialValue="BUSINESS"><Input /></Form.Item>
          <Form.Item name="technology_stack" label="Công nghệ"><Input.TextArea /></Form.Item>
          <Form.Item name="internet_exposed" label="Internet exposed" initialValue={false}><Select options={[{value:false,label:'Không'},{value:true,label:'Có'}]} /></Form.Item>
          <Form.Item name="has_api" label="Có API" initialValue={false}><Select options={[{value:false,label:'Không'},{value:true,label:'Có'}]} /></Form.Item>
        </>}
        {modal === 'db' && <>
          <Form.Item name="db_code" label="Mã CSDL" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="db_name" label="Tên CSDL" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="db_type" label="Loại CSDL" initialValue="ORACLE"><Input /></Form.Item>
          <Form.Item name="data_classification" label="Phân loại dữ liệu" initialValue="INTERNAL"><Select options={['PUBLIC','INTERNAL','CONFIDENTIAL','SECRET'].map(x=>({value:x,label:x}))} /></Form.Item>
          <Form.Item name="contains_personal_data" label="Dữ liệu cá nhân" initialValue={false}><Select options={[{value:false,label:'Không'},{value:true,label:'Có'}]} /></Form.Item>
          <Form.Item name="contains_financial_data" label="Dữ liệu tài chính" initialValue={false}><Select options={[{value:false,label:'Không'},{value:true,label:'Có'}]} /></Form.Item>
          <Form.Item name="size_gb" label="Dung lượng GB"><InputNumber min={0} style={{ width:'100%' }} /></Form.Item>
        </>}
        {modal === 'device' && <>
          <Form.Item name="device_code" label="Mã thiết bị" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="device_name" label="Tên thiết bị" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="information_system_id" label="Hệ thống"><Select allowClear options={systemOptions} /></Form.Item>
          <Form.Item name="device_type" label="Loại" initialValue="FIREWALL"><Select options={['FIREWALL','SWITCH','ROUTER','WAF','IPS','LOAD_BALANCER'].map(x=>({value:x,label:x}))} /></Form.Item>
          <Form.Item name="zone" label="Zone"><Input /></Form.Item><Form.Item name="ip_address" label="IP"><Input /></Form.Item>
          <Form.Item name="ha_enabled" label="HA" initialValue={false}><Select options={[{value:false,label:'Không'},{value:true,label:'Có'}]} /></Form.Item>
          <Form.Item name="internet_edge" label="Internet Edge" initialValue={false}><Select options={[{value:false,label:'Không'},{value:true,label:'Có'}]} /></Form.Item>
        </>}
      </Form>
    </Modal>
  </div>;
}
