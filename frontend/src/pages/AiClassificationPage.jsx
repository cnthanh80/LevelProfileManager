import React, { useEffect, useState } from 'react';
import { Alert, Button, Card, Checkbox, Col, Form, Input, InputNumber, List, Progress, Row, Select, Space, Statistic, Table, Tag, Typography, message } from 'antd';
import { RobotOutlined, ReloadOutlined } from '@ant-design/icons';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

const riskColor = { LOW: 'green', MEDIUM: 'blue', HIGH: 'orange', CRITICAL: 'red' };
const mismatchColor = { MATCH: 'green', UNDER_CLASSIFIED: 'red', OVER_CLASSIFIED: 'orange', NO_CURRENT_LEVEL: 'default' };

export default function AiClassificationPage({ profiles }) {
  const [dashboard, setDashboard] = useState(null);
  const [misclassified, setMisclassified] = useState([]);
  const [result, setResult] = useState(null);
  const [profileId, setProfileId] = useState(profiles?.[0]?.id);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadDashboard = async () => {
    setError('');
    try {
      const [d, m] = await Promise.all([api.aiClassificationDashboard(), api.aiMisclassifiedProfiles()]);
      setDashboard(d); setMisclassified(m || []);
    } catch (e) { setError(e.message || 'Không tải được dashboard AI'); }
  };
  const loadHistory = async (id = profileId) => {
    if (!id) return;
    try { setHistory(await api.aiRecommendationHistory(id)); } catch { setHistory([]); }
  };
  useEffect(() => { loadDashboard(); }, []);
  useEffect(() => { loadHistory(profileId); }, [profileId]);

  const classifyManual = async (values) => {
    setLoading(true);
    try { setResult(await api.aiClassifyLevel(values)); message.success('Đã phân loại dữ liệu đầu vào'); }
    catch (e) { message.error(e.message || 'Lỗi phân loại'); }
    finally { setLoading(false); }
  };
  const recommendProfile = async () => {
    if (!profileId) return;
    setLoading(true);
    try {
      const r = await api.aiRecommendProfile(profileId);
      setResult(r); message.success('Đã sinh khuyến nghị cấp độ cho hồ sơ');
      await Promise.all([loadDashboard(), loadHistory(profileId)]);
    } catch (e) { message.error(e.message || 'Lỗi khuyến nghị hồ sơ'); }
    finally { setLoading(false); }
  };

  return <Space direction="vertical" size="large" style={{ width: '100%' }}>
    <PageHeader title="AI Classification & Level Recommendation" subtitle="Gợi ý cấp độ, cảnh báo hồ sơ có nguy cơ phân loại thấp và sinh giải trình nghiệp vụ." />
    {error && <Alert type="error" showIcon message="Lỗi" description={error} action={<Button onClick={loadDashboard}>Tải lại</Button>} />}
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Lượt khuyến nghị" value={dashboard?.recommendation_count || 0} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Hồ sơ" value={dashboard?.profile_count || 0} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Statistic title="Nguy cơ phân loại thấp" value={dashboard?.under_classified_count || 0} valueStyle={{ color: (dashboard?.under_classified_count || 0) ? '#cf1322' : undefined }} /></Card></Col>
      <Col xs={24} sm={12} lg={6}><Card><Button icon={<ReloadOutlined />} onClick={loadDashboard}>Làm mới dashboard</Button></Card></Col>
    </Row>

    <Row gutter={[16, 16]}>
      <Col xs={24} lg={10}>
        <Card title={<><RobotOutlined /> Nhập tiêu chí phân loại</>}>
          <Form layout="vertical" onFinish={classifyManual} initialValues={{ user_count: 1000, transaction_per_day: 10000, confidentiality_impact: 'MEDIUM', integrity_impact: 'MEDIUM', availability_impact: 'MEDIUM', business_criticality: 'MEDIUM' }}>
            <Form.Item name="system_name" label="Tên hệ thống"><Input placeholder="Ví dụ: Core Banking, Mobile Banking" /></Form.Item>
            <Form.Item name="data_description" label="Mô tả dữ liệu"><Input.TextArea rows={3} placeholder="Dữ liệu cá nhân, tài chính, giao dịch, dữ liệu nhạy cảm..." /></Form.Item>
            <Row gutter={12}>
              <Col span={12}><Form.Item name="has_personal_data" valuePropName="checked"><Checkbox>Dữ liệu cá nhân</Checkbox></Form.Item></Col>
              <Col span={12}><Form.Item name="has_financial_data" valuePropName="checked"><Checkbox>Dữ liệu tài chính</Checkbox></Form.Item></Col>
              <Col span={12}><Form.Item name="has_sensitive_data" valuePropName="checked"><Checkbox>Dữ liệu nhạy cảm</Checkbox></Form.Item></Col>
              <Col span={12}><Form.Item name="has_state_secret_or_highly_sensitive_data" valuePropName="checked"><Checkbox>Dữ liệu đặc biệt nhạy cảm</Checkbox></Form.Item></Col>
              <Col span={12}><Form.Item name="internet_exposed" valuePropName="checked"><Checkbox>Công khai Internet</Checkbox></Form.Item></Col>
              <Col span={12}><Form.Item name="third_party_connections" valuePropName="checked"><Checkbox>Kết nối bên thứ ba/API</Checkbox></Form.Item></Col>
              <Col span={12}><Form.Item name="cross_org_connections" valuePropName="checked"><Checkbox>Liên thông nhiều đơn vị</Checkbox></Form.Item></Col>
            </Row>
            <Row gutter={12}>
              <Col span={12}><Form.Item name="user_count" label="Người dùng"><InputNumber min={0} style={{ width: '100%' }} /></Form.Item></Col>
              <Col span={12}><Form.Item name="transaction_per_day" label="Giao dịch/ngày"><InputNumber min={0} style={{ width: '100%' }} /></Form.Item></Col>
            </Row>
            {['confidentiality_impact','integrity_impact','availability_impact','business_criticality'].map(k => <Form.Item key={k} name={k} label={k}><Select options={['LOW','MEDIUM','HIGH','CRITICAL'].map(v => ({ value: v, label: v }))} /></Form.Item>)}
            <Button type="primary" htmlType="submit" loading={loading}>Phân loại</Button>
          </Form>
        </Card>
      </Col>
      <Col xs={24} lg={14}>
        <Card title="Khuyến nghị theo hồ sơ" extra={<Space><Select style={{ width: 320 }} value={profileId} onChange={setProfileId} options={(profiles || []).map(p => ({ value: p.id, label: p.profile_code }))} /><Button type="primary" onClick={recommendProfile} loading={loading}>Sinh khuyến nghị</Button></Space>}>
          {result ? <Space direction="vertical" style={{ width: '100%' }}>
            <Row gutter={[16, 16]}>
              <Col span={8}><Card><Statistic title="Cấp độ khuyến nghị" value={result.recommended_level} /></Card></Col>
              <Col span={8}><Card><Statistic title="Độ tin cậy" value={result.confidence_score} suffix="%" /></Card></Col>
              <Col span={8}><Card><Statistic title="Điểm rủi ro" value={result.risk_score} /></Card></Col>
            </Row>
            <Space><Tag color={riskColor[result.risk_band] || 'default'}>{result.risk_band}</Tag><Tag color={mismatchColor[result.mismatch_status] || 'default'}>{result.mismatch_status}</Tag></Space>
            <Typography.Paragraph>{result.explanation}</Typography.Paragraph>
            <List header="Lý do" dataSource={result.reasons || []} renderItem={(x) => <List.Item>{x}</List.Item>} />
            <List header="Khuyến nghị xử lý" dataSource={result.recommended_actions || []} renderItem={(x) => <List.Item>{x}</List.Item>} />
          </Space> : <JsonView title="Kết quả" data={result} />}
        </Card>
      </Col>
    </Row>

    <Row gutter={[16, 16]}>
      <Col xs={24} lg={12}>
        <Card title="Hồ sơ có nguy cơ phân loại thấp">
          <Table size="small" rowKey="recommendation_id" dataSource={misclassified} columns={[
            { title: 'Hồ sơ', dataIndex: 'profile_id' },
            { title: 'Hiện tại', dataIndex: 'current_level' },
            { title: 'Khuyến nghị', dataIndex: 'recommended_level' },
            { title: 'Risk', dataIndex: 'risk_band', render: v => <Tag color={riskColor[v]}>{v}</Tag> },
            { title: 'Điểm', dataIndex: 'risk_score' },
            { title: 'Tin cậy', dataIndex: 'confidence_score', render: v => <Progress percent={v} size="small" /> },
          ]} />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Lịch sử khuyến nghị hồ sơ đang chọn">
          <Table size="small" rowKey="id" dataSource={history} columns={[
            { title: 'ID', dataIndex: 'id', width: 70 },
            { title: 'Hiện tại', dataIndex: 'current_level' },
            { title: 'Khuyến nghị', dataIndex: 'recommended_level' },
            { title: 'Risk', dataIndex: 'risk_band', render: v => <Tag color={riskColor[v]}>{v}</Tag> },
            { title: 'Trạng thái', dataIndex: 'mismatch_status', render: v => <Tag color={mismatchColor[v]}>{v}</Tag> },
          ]} />
        </Card>
      </Col>
    </Row>
  </Space>;
}
