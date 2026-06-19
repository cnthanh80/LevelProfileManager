import { Button, Card, Checkbox, Col, Form, InputNumber, Row, Select, Space, Table, message } from 'antd';
import { useState } from 'react';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

export default function CompliancePage({ profiles }) {
  const [classification, setClassification] = useState(null); const [profileId, setProfileId] = useState(profiles?.[0]?.id); const [result, setResult] = useState({});
  const classify = async (v) => { setClassification(await api.classifyLevel(v)); };
  const loadProfile = async () => { if (!profileId) return; const [score, risk, readiness, gap, suggest] = await Promise.allSettled([api.complianceScore(profileId), api.risk(profileId), api.readiness(profileId), api.gapAnalysis(profileId), api.suggestLevel(profileId)]); const val=(x)=>x.status==='fulfilled'?x.value:null; setResult({ score:val(score), risk:val(risk), readiness:val(readiness), gap:val(gap), suggest:val(suggest) }); };
  const run = async () => { await api.runAssessment(profileId); message.success('Đã chạy assessment'); loadProfile(); };
  return <>
    <PageHeader title="Compliance Engine" subtitle="Gợi ý cấp độ, phân tích GAP, risk score và readiness score." />
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
        <Button type="primary" htmlType="submit">Gợi ý cấp độ</Button>
      </Form></Card></Col>
      <Col xs={24} lg={14}><JsonView title="Kết quả gợi ý" data={classification} /></Col>
    </Row>
    <Card title="Đánh giá hồ sơ" style={{ marginTop: 16 }} extra={<Space><Select style={{width:360}} value={profileId} onChange={setProfileId} options={(profiles||[]).map(p=>({value:p.id,label:p.profile_code}))} /><Button onClick={loadProfile}>Tải đánh giá</Button><Button type="primary" onClick={run}>Chạy assessment</Button></Space>}>
      <Row gutter={[16,16]}><Col span={8}><JsonView title="Score" data={result.score} /></Col><Col span={8}><JsonView title="Risk" data={result.risk} /></Col><Col span={8}><JsonView title="Readiness" data={result.readiness} /></Col></Row>
      <Table style={{marginTop:16}} rowKey="requirement_id" dataSource={result.gap?.gaps || []} columns={[{title:'Mã',dataIndex:'code'},{title:'Yêu cầu',dataIndex:'title'},{title:'Nhóm',dataIndex:'group_name'},{title:'Bắt buộc',dataIndex:'is_mandatory',render:v=>v?'Có':'Không'},{title:'Trạng thái',dataIndex:'status'}]} />
    </Card>
  </>;
}
