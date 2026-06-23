import { Alert, Button, Card, Checkbox, Descriptions, List, Modal, Select, Space, Table, Tag, Typography, message } from 'antd';
import React, { useEffect, useState } from 'react';
import PageHeader from '../components/PageHeader';
import { api, downloadFile } from '../api/client';

function pickItems(value) { return Array.isArray(value?.items) ? value.items : Array.isArray(value) ? value : []; }
function fmtSize(v) {
  const n = Number(v || 0);
  if (n > 1024 * 1024) return `${(n / 1024 / 1024).toFixed(2)} MB`;
  if (n > 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${n} B`;
}

export default function GovernmentDossierPage({ profiles }) {
  const [profileId, setProfileId] = useState(profiles?.[0]?.id);
  const [includeEvidence, setIncludeEvidence] = useState(true);
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState({});
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setError('');
    try {
      const [s, d] = await Promise.allSettled([api.governmentDossierSummary(), api.governmentDossiers({ limit: 100 })]);
      if (s.status === 'fulfilled') setSummary(s.value || {});
      if (d.status === 'fulfilled') setItems(pickItems(d.value));
    } catch (e) {
      setError(e.message || 'Không tải được danh sách bộ hồ sơ');
    }
  };

  useEffect(() => { load(); }, []);

  const generate = async () => {
    if (!profileId) { message.warning('Vui lòng chọn hồ sơ cấp độ.'); return; }
    setLoading(true); setError('');
    try {
      const data = await api.generateGovernmentDossierPack(profileId, { include_evidence: includeEvidence, notes: 'Generated from UI Phase 42.0' });
      setDetail(data);
      message.success('Đã sinh bộ hồ sơ cấp độ.');
      await load();
    } catch (e) {
      setError(e.message || 'Không sinh được bộ hồ sơ');
      message.error(e.message || 'Không sinh được bộ hồ sơ');
    } finally { setLoading(false); }
  };

  const openDetail = async (id) => {
    try {
      const data = await api.governmentDossier(id);
      setDetail(data);
    } catch (e) { message.error(e.message || 'Không tải được chi tiết'); }
  };

  const downloadZip = async (r) => {
    try { await downloadFile(`/dossiers/${r.id}/download`, r.package_filename); }
    catch (e) { message.error(e.message || 'Không tải được ZIP'); }
  };
  const downloadSingleFile = async (f) => {
    try { await downloadFile(`/dossier-files/${f.id}/download`, f.file_name); }
    catch (e) { message.error(e.message || 'Không tải được file'); }
  };

  return <>
    <PageHeader
      title="Government Dossier Pack"
      subtitle="Sinh bộ hồ sơ cấp độ theo mẫu DOCX đang kích hoạt trong Quản lý mẫu biểu; nếu chưa có mẫu active, hệ thống dùng mẫu mặc định."
      actions={<Space>
        <Select style={{ width: 280 }} value={profileId} onChange={setProfileId} options={(profiles || []).map(p => ({ value: p.id, label: `${p.profile_code} · Level ${p.proposed_level || ''}` }))} />
        <Checkbox checked={includeEvidence} onChange={e => setIncludeEvidence(e.target.checked)}>Kèm minh chứng</Checkbox>
        <Button type="primary" loading={loading} onClick={generate}>Sinh bộ hồ sơ</Button>
      </Space>}
    />
    {error ? <Alert type="error" showIcon message="Lỗi" description={error} style={{ marginBottom: 16 }} /> : null}
    <Card style={{ marginBottom: 16 }}>
      <Descriptions column={4} size="small">
        <Descriptions.Item label="Tổng bộ hồ sơ">{summary.total_dossiers || 0}</Descriptions.Item>
        <Descriptions.Item label="Tổng file sinh ra">{summary.generated_files || 0}</Descriptions.Item>
        <Descriptions.Item label="Dung lượng ZIP">{fmtSize(summary.total_package_size)}</Descriptions.Item>
        <Descriptions.Item label="Phiên bản">Phase 42.1 / v4.3</Descriptions.Item>
      </Descriptions>
    </Card>
    <Card title="Danh sách bộ hồ sơ đã sinh">
      <Table rowKey="id" dataSource={items} loading={loading} columns={[
        { title: 'Mã bộ hồ sơ', dataIndex: 'dossier_code' },
        { title: 'Hồ sơ', dataIndex: 'profile_id', render: v => `#${v}` },
        { title: 'Phiên bản', dataIndex: 'version', render: v => <Tag color="blue">v{v}</Tag> },
        { title: 'Trạng thái', dataIndex: 'status', render: v => <Tag color="green">{v}</Tag> },
        { title: 'Minh chứng', dataIndex: 'included_evidence_count' },
        { title: 'Dung lượng', dataIndex: 'package_size', render: fmtSize },
        { title: 'Thời gian', dataIndex: 'created_at', render: v => v ? new Date(v).toLocaleString() : '' },
        { title: 'Thao tác', render: (_, r) => <Space><Button size="small" onClick={() => openDetail(r.id)}>Chi tiết</Button><Button size="small" type="primary" onClick={() => downloadZip(r)}>Download ZIP</Button></Space> },
      ]} />
    </Card>
    <Modal title="Chi tiết bộ hồ sơ" open={!!detail} onCancel={() => setDetail(null)} footer={null} width={850}>
      {detail ? <>
        <Descriptions bordered size="small" column={2} style={{ marginBottom: 16 }}>
          <Descriptions.Item label="Mã bộ hồ sơ">{detail.dossier_code}</Descriptions.Item>
          <Descriptions.Item label="Phiên bản">v{detail.version}</Descriptions.Item>
          <Descriptions.Item label="Tên gói ZIP">{detail.package_filename}</Descriptions.Item>
          <Descriptions.Item label="Dung lượng">{fmtSize(detail.package_size)}</Descriptions.Item>
          <Descriptions.Item label="Checksum" span={2}><Typography.Text copyable>{detail.checksum_sha256}</Typography.Text></Descriptions.Item>
        </Descriptions>
        <List
          bordered
          dataSource={detail.files || []}
          renderItem={f => <List.Item actions={[<Button key="download" size="small" onClick={() => downloadSingleFile(f)}>Tải file</Button>]}>
            <List.Item.Meta title={`${f.sort_order}. ${f.display_name}`} description={`${f.file_name} · ${fmtSize(f.file_size)} · ${f.file_type}`} />
          </List.Item>}
        />
        <Space style={{ marginTop: 16 }}>
          <Button type="primary" onClick={() => downloadZip(detail)}>Download ZIP</Button>
          <Button onClick={async () => { const data = await api.regenerateGovernmentDossierPack(detail.id, { include_evidence: includeEvidence }); setDetail(data); await load(); message.success('Đã sinh lại bộ hồ sơ phiên bản mới.'); }}>Regenerate</Button>
        </Space>
      </> : null}
    </Modal>
  </>;
}
