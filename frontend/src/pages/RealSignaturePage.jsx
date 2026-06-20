import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Form, Input, Modal, Row, Select, Space, Statistic, Table, Tag, message } from 'antd';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

function pickItems(x) { return Array.isArray(x?.items) ? x.items : Array.isArray(x) ? x : []; }

export default function RealSignaturePage({ profiles = [] }) {
  const [status, setStatus] = useState({});
  const [providers, setProviders] = useState([]);
  const [requests, setRequests] = useState([]);
  const [versions, setVersions] = useState([]);
  const [profileId, setProfileId] = useState(profiles?.[0]?.id);
  const [versionId, setVersionId] = useState();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => { if (!profileId && profiles?.[0]?.id) setProfileId(profiles[0].id); }, [profiles]);
  useEffect(() => { load(); }, []);
  useEffect(() => { if (profileId) loadVersions(); }, [profileId]);

  async function load() {
    setLoading(true);
    try {
      const [st, p, r] = await Promise.all([api.signatureGatewayStatus(), api.signatureProviders({ limit: 100 }), api.signatureRequests({ limit: 100 })]);
      setStatus(st || {}); setProviders(pickItems(p)); setRequests(pickItems(r));
    } catch (e) { message.error(e.message || 'Không tải được gateway ký số'); }
    finally { setLoading(false); }
  }

  async function loadVersions() {
    try {
      const v = await api.profileVersions(profileId, { limit: 50 });
      const items = pickItems(v); setVersions(items); if (items?.[0]) setVersionId(items[0].id);
    } catch {}
  }

  async function seedProviders() {
    try { await api.seedSignatureProviders(); message.success('Đã seed nhà cung cấp ký số'); load(); } catch (e) { message.error(e.message); }
  }

  async function createRequest() {
    if (!versionId) { message.warning('Chưa chọn phiên bản hồ sơ'); return; }
    form.setFieldsValue({ sign_method: 'MOCK_REMOTE', provider_id: providers?.[0]?.id, signer_role: 'Lãnh đạo phê duyệt', note: 'Yêu cầu ký số qua gateway v3.2' });
    Modal.confirm({
      title: 'Tạo yêu cầu ký số qua gateway',
      width: 720,
      content: <Form form={form} layout="vertical">
        <Form.Item name="provider_id" label="Nhà cung cấp"><Select options={providers.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} /></Form.Item>
        <Form.Item name="sign_method" label="Phương thức"><Select options={[{ value: 'MOCK_REMOTE', label: 'Mock Remote Signing' }, { value: 'REMOTE_SIGNING', label: 'Remote Signing' }, { value: 'HSM', label: 'HSM Gateway' }, { value: 'USB_TOKEN', label: 'USB Token' }]} /></Form.Item>
        <Form.Item name="signer_name" label="Người ký"><Input placeholder="Để trống dùng tài khoản hiện tại" /></Form.Item>
        <Form.Item name="signer_role" label="Vai trò"><Input /></Form.Item>
        <Form.Item name="note" label="Ghi chú"><Input.TextArea rows={3} /></Form.Item>
      </Form>,
      onOk: async () => { const values = await form.validateFields(); await api.createRealSignRequest(versionId, values); message.success('Đã tạo yêu cầu ký số'); load(); }
    });
  }

  async function simulate(row) {
    try { await api.simulateSignatureCallback(row.request_code); message.success('Đã mô phỏng callback ký thành công'); load(); } catch (e) { message.error(e.message); }
  }

  return <>
    <PageHeader title="Ký số thực tế / Signature Gateway" subtitle="Nền tảng tích hợp Remote Signing, USB Token, HSM và callback từ CA. Bản v3.2 cung cấp adapter foundation và mock remote signing." actions={<Space><Button onClick={seedProviders}>Seed nhà cung cấp</Button><Button type="primary" onClick={createRequest}>Tạo yêu cầu ký</Button></Space>} />
    <Row gutter={16} style={{ marginBottom: 16 }}>
      <Col span={6}><Card><Statistic title="Nhà cung cấp" value={status.providers_total || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Đang hoạt động" value={status.active_providers || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Yêu cầu ký" value={status.requests_total || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Đã ký" value={status.signed_requests || 0} /></Card></Col>
    </Row>
    <Card style={{ marginBottom: 16 }}>
      <Space wrap>
        <span>Hồ sơ:</span>
        <Select style={{ minWidth: 360 }} value={profileId} onChange={setProfileId} options={(profiles || []).map(p => ({ value: p.id, label: `${p.profile_code} - cấp ${p.proposed_level}` }))} />
        <span>Phiên bản:</span>
        <Select style={{ minWidth: 240 }} value={versionId} onChange={setVersionId} options={versions.map(v => ({ value: v.id, label: `v${v.version_no} - ${v.title}` }))} />
        <Button onClick={load}>Tải lại</Button>
      </Space>
    </Card>
    <Row gutter={16}>
      <Col span={12}>
        <Card title="Nhà cung cấp ký số" loading={loading}>
          <Table rowKey="id" dataSource={providers} pagination={{ pageSize: 6 }} columns={[
            { title: 'Mã', dataIndex: 'code' },
            { title: 'Tên', dataIndex: 'name' },
            { title: 'Loại', dataIndex: 'provider_type', render: v => <Tag>{v}</Tag> },
            { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={v === 'ACTIVE' ? 'green' : 'default'}>{v}</Tag> },
          ]} />
        </Card>
      </Col>
      <Col span={12}>
        <Card title="Ghi chú production"><JsonView data={status} /></Card>
      </Col>
    </Row>
    <Card title="Yêu cầu ký số" style={{ marginTop: 16 }}>
      <Table rowKey="id" dataSource={requests} pagination={{ pageSize: 8 }} columns={[
        { title: 'Request', dataIndex: 'request_code' },
        { title: 'Version', dataIndex: 'version_id' },
        { title: 'Method', dataIndex: 'sign_method', render: v => <Tag>{v}</Tag> },
        { title: 'Status', dataIndex: 'status', render: v => <Tag color={v === 'SIGNED' ? 'green' : v === 'FAILED' ? 'red' : 'gold'}>{v}</Tag> },
        { title: 'Hash', dataIndex: 'document_hash', render: v => <code>{String(v).slice(0, 12)}...</code> },
        { title: 'Thao tác', render: (_, r) => <Button disabled={r.status === 'SIGNED'} onClick={() => simulate(r)}>Mock callback</Button> },
      ]} />
    </Card>
  </>;
}
