import { Button, Card, Col, Form, Input, Modal, Row, Select, Space, Statistic, Table, Tag, Timeline, message } from 'antd';
import React, { useEffect, useState } from 'react';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api, downloadUrl } from '../api/client';

function pickItems(x) { return Array.isArray(x?.items) ? x.items : Array.isArray(x) ? x : []; }

export default function DigitalDossierPage({ profiles = [] }) {
  const [profileId, setProfileId] = useState(profiles?.[0]?.id);
  const [summary, setSummary] = useState({});
  const [versions, setVersions] = useState([]);
  const [signatures, setSignatures] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [compareResult, setCompareResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [signForm] = Form.useForm();

  useEffect(() => { if (!profileId && profiles?.[0]?.id) setProfileId(profiles[0].id); }, [profiles]);
  useEffect(() => { if (profileId) load(); }, [profileId]);

  async function load() {
    setLoading(true);
    try {
      const [s, v, sg] = await Promise.all([
        api.dossierSummary(profileId),
        api.profileVersions(profileId, { limit: 100 }),
        api.profileSignatures(profileId, { limit: 100 }),
      ]);
      setSummary(s || {}); setVersions(pickItems(v)); setSignatures(pickItems(sg));
    } catch (e) { message.error(e.message || 'Không tải được hồ sơ điện tử'); }
    finally { setLoading(false); }
  }

  async function createVersion() {
    try {
      const payload = { title: `Phiên bản hồ sơ điện tử ${new Date().toLocaleString('vi-VN')}`, change_summary: 'Tạo phiên bản từ giao diện web' };
      await api.createProfileVersion(profileId, payload);
      message.success('Đã tạo phiên bản hồ sơ điện tử'); load();
    } catch (e) { message.error(e.message); }
  }

  async function viewVersion(row) {
    try { setSelectedVersion(await api.profileVersion(row.id)); } catch (e) { message.error(e.message); }
  }

  async function signVersion(row) {
    signForm.setFieldsValue({ signer_name: '', signer_role: 'Lãnh đạo phê duyệt', sign_method: 'MOCK', comment: 'Ký số mô phỏng hồ sơ đề xuất cấp độ' });
    Modal.confirm({
      title: `Ký số mô phỏng phiên bản ${row.version_no}`,
      width: 720,
      content: <Form form={signForm} layout="vertical">
        <Form.Item name="signer_name" label="Người ký"><Input placeholder="Để trống để dùng tài khoản hiện tại" /></Form.Item>
        <Form.Item name="signer_role" label="Vai trò ký"><Input /></Form.Item>
        <Form.Item name="sign_method" label="Phương thức"><Select options={[{ value: 'MOCK', label: 'Mock signing' }, { value: 'USB_TOKEN', label: 'USB Token - placeholder' }, { value: 'REMOTE_SIGNING', label: 'Remote Signing - placeholder' }]} /></Form.Item>
        <Form.Item name="comment" label="Ý kiến"><Input.TextArea rows={3} /></Form.Item>
      </Form>,
      onOk: async () => { const values = await signForm.validateFields(); await api.signProfileVersion(row.id, values); message.success('Đã ký số mô phỏng'); load(); }
    });
  }

  async function compareLatest() {
    if (versions.length < 2) { message.info('Cần ít nhất 2 phiên bản để so sánh'); return; }
    try { setCompareResult(await api.compareProfileVersions(versions[1].id, versions[0].id)); } catch (e) { message.error(e.message); }
  }

  return <>
    <PageHeader title="Hồ sơ điện tử & ký số" subtitle="Quản lý phiên bản hồ sơ, so sánh thay đổi, ký số mô phỏng và lưu bằng chứng hash." actions={<Space><Button onClick={compareLatest}>So sánh 2 bản mới nhất</Button><Button type="primary" onClick={createVersion}>Tạo phiên bản</Button></Space>} />
    <Card style={{ marginBottom: 16 }}>
      <Space wrap>
        <span>Chọn hồ sơ:</span>
        <Select style={{ minWidth: 360 }} value={profileId} onChange={setProfileId} options={(profiles || []).map(p => ({ value: p.id, label: `${p.profile_code} - cấp ${p.proposed_level}` }))} />
        <Button onClick={load}>Tải lại</Button>
      </Space>
    </Card>
    <Row gutter={16} style={{ marginBottom: 16 }}>
      <Col span={6}><Card><Statistic title="Phiên bản" value={summary.total_versions || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Chữ ký" value={summary.total_signatures || 0} /></Card></Col>
      <Col span={6}><Card><Statistic title="Bản mới nhất" value={summary.latest_version_no || 0} prefix="v" /></Card></Col>
      <Col span={6}><Card><Statistic title="Trạng thái" value={summary.signed ? 'Đã ký' : 'Chưa ký'} /></Card></Col>
    </Row>
    <Row gutter={16}>
      <Col span={15}>
        <Card title="Phiên bản hồ sơ" loading={loading}>
          <Table rowKey="id" dataSource={versions} pagination={{ pageSize: 8 }} columns={[
            { title: 'Version', dataIndex: 'version_no', render: v => <Tag color="blue">v{v}</Tag> },
            { title: 'Tiêu đề', dataIndex: 'title' },
            { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color={v === 'SIGNED' ? 'green' : 'gold'}>{v}</Tag> },
            { title: 'Hash', dataIndex: 'snapshot_hash', render: v => <code>{String(v).slice(0, 14)}...</code> },
            { title: 'Thao tác', render: (_, r) => <Space><Button onClick={() => viewVersion(r)}>Xem snapshot</Button><Button type="primary" onClick={() => signVersion(r)}>Ký</Button></Space> }
          ]} />
        </Card>
        {compareResult && <Card title="Kết quả so sánh phiên bản" style={{ marginTop: 16 }} extra={<Button onClick={() => setCompareResult(null)}>Đóng</Button>}><JsonView data={compareResult} /></Card>}
      </Col>
      <Col span={9}>
        <Card title="Timeline ký số">
          <Timeline items={signatures.map(s => ({ color: 'green', children: <div><b>{s.signer_name}</b> · {s.signer_role}<br/><Tag>{s.sign_method}</Tag> <code>{String(s.signature_hash).slice(0, 12)}...</code><br/><a href={downloadUrl(`/profile-signatures/${s.id}/download`)} target="_blank">Tải bằng chứng ký</a></div> }))} />
        </Card>
      </Col>
    </Row>
    <Modal title="Snapshot hồ sơ điện tử" open={!!selectedVersion} onCancel={() => setSelectedVersion(null)} footer={<Button onClick={() => setSelectedVersion(null)}>Đóng</Button>} width="80%">
      <JsonView data={selectedVersion || {}} />
    </Modal>
  </>;
}
