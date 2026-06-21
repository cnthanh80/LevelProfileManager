import { Alert, Button, Card, Checkbox, Col, Form, InputNumber, Row, Select, Space, Table, Typography, message } from 'antd';
import React, { useState } from 'react';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api, hasToken } from '../api/client';

function errorText(e) {
  if (!e) return 'Không xác định được lỗi.';
  if (typeof e.message === 'string') return e.message;
  return String(e);
}

export default function CompliancePage({ profiles }) {
  const [classification, setClassification] = useState(null);
  const [profileId, setProfileId] = useState(profiles?.[0]?.id);
  const [result, setResult] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const ensureLogin = () => {
    if (!hasToken()) {
      const msg = 'Anh/chị chưa đăng nhập hoặc phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.';
      setError(msg);
      message.error(msg);
      return false;
    }
    return true;
  };

  const classify = async (v) => {
    if (!ensureLogin()) return;
    setLoading(true);
    setError('');
    try {
      const data = await api.classifyLevel(v);
      setClassification(data);
      message.success('Đã sinh gợi ý cấp độ.');
    } catch (e) {
      const msg = errorText(e);
      setError(msg);
      setClassification(null);
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const loadProfile = async () => {
    if (!profileId) return;
    if (!ensureLogin()) return;
    setLoading(true);
    setError('');
    try {
      const [score, risk, readiness, gap, suggest] = await Promise.all([
        api.complianceScore(profileId),
        api.risk(profileId),
        api.readiness(profileId),
        api.gapAnalysis(profileId),
        api.suggestLevel(profileId),
      ]);
      setResult({ score, risk, readiness, gap, suggest });
      message.success('Đã tải đánh giá hồ sơ.');
    } catch (e) {
      const msg = errorText(e);
      setError(msg);
      setResult({});
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const run = async () => {
    if (!profileId) return;
    if (!ensureLogin()) return;
    setLoading(true);
    setError('');
    try {
      const assessment = await api.runAssessment(profileId);
      message.success('Đã chạy assessment thành công.');
      await loadProfile();
      setResult((prev) => ({ ...prev, assessment }));
    } catch (e) {
      const msg = errorText(e);
      setError(msg);
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return <>
    <PageHeader title="Compliance Engine" subtitle="Gợi ý cấp độ, phân tích GAP, risk score và readiness score." />
    {error && <Alert type="error" showIcon message="Compliance Engine chưa xử lý thành công" description={error} style={{ marginBottom: 16 }} />}
    <Row gutter={[16,16]}>
      <Col xs={24} lg={10}><Card title="Auto Classification"><Form layout="vertical" onFinish={classify} initialValues={{ user_count: 1000, transaction_per_day: 5000, downtime_impact:'MEDIUM', confidentiality_impact:'MEDIUM', integrity_impact:'MEDIUM', availability_impact:'MEDIUM' }}>
        <Form.Item name="has_personal_data" valuePropName="checked"><Checkbox>Dữ liệu cá nhân</Checkbox></Form.Item>
        <Form.Item name="has_financial_data" valuePropName="checked"><Checkbox>Dữ liệu tài chính</Checkbox></Form.Item>
        <Form.Item name="has_sensitive_data" valuePropName="checked"><Checkbox>Dữ liệu nhạy cảm</Checkbox></Form.Item>
        <Form.Item name="internet_exposed" valuePropName="checked"><Checkbox>Có kết nối Internet</Checkbox></Form.Item>
        <Form.Item name="third_party_connections" valuePropName="checked"><Checkbox>Kết nối bên thứ ba/API</Checkbox></Form.Item>
        <Form.Item name="user_count" label="Số người dùng"><InputNumber min={0} style={{width:'100%'}} /></Form.Item>
        <Form.Item name="transaction_per_day" label="Giao dịch/ngày"><InputNumber min={0} style={{width:'100%'}} /></Form.Item>
        {['downtime_impact','confidentiality_impact','integrity_impact','availability_impact'].map(k => <Form.Item key={k} name={k} label={k}><Select options={['LOW','MEDIUM','HIGH','CRITICAL'].map(v=>({value:v,label:v}))} /></Form.Item>)}
        <Button type="primary" htmlType="submit" loading={loading}>Gợi ý cấp độ</Button>
      </Form></Card></Col>
      <Col xs={24} lg={14}>
        <JsonView title="Kết quả gợi ý" data={classification} />
        {classification && <Alert style={{ marginTop: 16 }} type="success" showIcon message={`Cấp độ gợi ý: ${classification.recommended_level || classification.level || 'N/A'}`} description={classification.explanation || 'Kết quả chi tiết hiển thị trong JSON phía trên.'} />}
      </Col>
    </Row>
    <Card title="Đánh giá hồ sơ" style={{ marginTop: 16 }} extra={<Space><Select style={{width:360}} value={profileId} onChange={setProfileId} options={(profiles||[]).map(p=>({value:p.id,label:p.profile_code}))} /><Button onClick={loadProfile} loading={loading}>Tải đánh giá</Button><Button type="primary" onClick={run} loading={loading}>Chạy assessment</Button></Space>}>
      <Row gutter={[16,16]}>
        <Col span={8}><JsonView title="Score" data={result.score} /></Col>
        <Col span={8}><JsonView title="Risk" data={result.risk} /></Col>
        <Col span={8}><JsonView title="Readiness" data={result.readiness} /></Col>
      </Row>
      <Row gutter={[16,16]} style={{ marginTop: 16 }}>
        <Col span={12}><JsonView title="Gợi ý cấp độ theo hồ sơ" data={result.suggest} /></Col>
        <Col span={12}><JsonView title="Assessment vừa chạy" data={result.assessment} /></Col>
      </Row>
      <Typography.Title level={5} style={{ marginTop: 16 }}>Danh sách GAP</Typography.Title>
      <Table style={{marginTop:8}} rowKey={(r) => r.requirement_id || r.code || r.title} dataSource={result.gap?.gaps || []} columns={[{title:'Mã',dataIndex:'code'},{title:'Yêu cầu',dataIndex:'title'},{title:'Nhóm',dataIndex:'group_name'},{title:'Bắt buộc',dataIndex:'is_mandatory',render:v=>v?'Có':'Không'},{title:'Trạng thái',dataIndex:'status'}]} />
    </Card>
  </>;
}
