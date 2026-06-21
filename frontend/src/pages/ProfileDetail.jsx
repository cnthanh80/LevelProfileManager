import { Alert, Button, Card, Col, Descriptions, Form, Input, InputNumber, Progress, Row, Select, Space, Tabs, Table, Timeline, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import React, { useEffect, useState } from 'react';
import StatusTag from '../components/StatusTag';
import JsonView from '../components/JsonView';
import { api, downloadFile, getToken } from '../api/client';

export default function ProfileDetail({ profile, reload }) {
  const [loading, setLoading] = useState(false); const [data, setData] = useState({}); const [commentForm] = Form.useForm(); const [uploadForm] = Form.useForm();
  const load = async () => {
    setLoading(true);
    try {
      const [workflow, history, comments, checklist, summary, evidence, score, risk, readiness, gap, reviews] = await Promise.allSettled([
        api.workflow(profile.id), api.workflowHistory(profile.id), api.comments(profile.id), api.checklist(profile.id), api.profileComplianceSummary(profile.id), api.profileEvidence(profile.id), api.complianceScore(profile.id), api.risk(profile.id), api.readiness(profile.id), api.gapAnalysis(profile.id), api.profilePeriodicReviews(profile.id)
      ]);
      const val = (r, d) => r.status === 'fulfilled' ? r.value : d;
      setData({ workflow: val(workflow, null), history: val(history, []), comments: val(comments, []), checklist: val(checklist, []), summary: val(summary, null), evidence: val(evidence, []), score: val(score, null), risk: val(risk, null), readiness: val(readiness, null), gap: val(gap, null), reviews: val(reviews, {items:[]}) });
    } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [profile.id]);

  const generateChecklist = async () => { await api.generateChecklist(profile.id); message.success('Đã sinh checklist'); load(); };
  const updateAnswer = async (id, values) => { await api.updateChecklistAnswer(id, values); message.success('Đã cập nhật checklist'); load(); };
  const transition = async (action) => { await api.transitionWorkflow(profile.id, { action, comment: `Thực hiện ${action} từ giao diện` }); message.success('Đã chuyển trạng thái'); await load(); reload?.(); };
  const addComment = async () => { const v = await commentForm.validateFields(); await api.addComment(profile.id, { ...v, workflow_state: profile.status, action: 'comment' }); commentForm.resetFields(); message.success('Đã thêm ý kiến'); load(); };
  const runAssessment = async () => { await api.runAssessment(profile.id); message.success('Đã chạy đánh giá'); load(); };
  const generateReview = async () => { await api.generateNextReview(profile.id, { months: 12 }); message.success('Đã tạo lịch rà soát'); load(); };
  const exportDoc = async (document_type, gov = false) => { gov ? await api.generateGovernmentDocument(profile.id, { document_type, file_format: 'docx' }) : await api.exportProfile(profile.id, { document_type, file_format: 'docx' }); message.success('Đã sinh tài liệu'); };
  const uploadEvidence = async (values) => {
    const file = values.file?.fileList?.[0]?.originFileObj;
    if (!file) return message.error('Chọn file');
    const fd = new FormData(); fd.append('profile_id', profile.id); fd.append('document_type', values.document_type || 'OTHER'); fd.append('title', values.title || file.name); if (values.checklist_answer_id) fd.append('checklist_answer_id', values.checklist_answer_id); fd.append('file', file);
    await api.uploadEvidence(fd); uploadForm.resetFields(); message.success('Đã upload minh chứng'); load();
  };
  const download = async (path, filename) => { try { const res = await downloadFile(path, filename); message.success(`Đã tải: ${res.filename}`); } catch(e) { message.error(e.message || 'Không tải được tài liệu'); } };

  const checklistColumns = [
    { title: 'Mã', dataIndex: ['requirement','code'], render: (_, r) => r.requirement?.code || r.code },
    { title: 'Yêu cầu', dataIndex: ['requirement','title'], render: (_, r) => r.requirement?.title || r.title, width: 280 },
    { title: 'Nhóm', dataIndex: ['requirement','group_name'], render: (_, r) => r.requirement?.group_name || r.group_name },
    { title: 'Bắt buộc', dataIndex: ['requirement','is_mandatory'], render: (_, r) => (r.requirement?.is_mandatory ?? r.is_mandatory) ? 'Có' : 'Không' },
    { title: 'Trạng thái', dataIndex: 'status', render: (v) => <StatusTag value={v} /> },
    { title: 'Minh chứng', dataIndex: 'evidence_count' },
    { title: 'Cập nhật', render: (_, r) => <Space><Button onClick={() => updateAnswer(r.id, { status: 'COMPLIANT' })}>Đáp ứng</Button><Button onClick={() => updateAnswer(r.id, { status: 'NON_COMPLIANT' })}>Chưa</Button><Button onClick={() => updateAnswer(r.id, { status: 'NOT_APPLICABLE' })}>N/A</Button></Space> }
  ];

  return <Space direction="vertical" size="large" style={{ width: '100%' }}>
    <Descriptions bordered size="small" column={2} title="Thông tin hồ sơ">
      <Descriptions.Item label="Mã hồ sơ">{profile.profile_code}</Descriptions.Item><Descriptions.Item label="Cấp độ">Cấp {profile.proposed_level}</Descriptions.Item>
      <Descriptions.Item label="Trạng thái"><StatusTag value={data.workflow?.current_status || profile.status} /></Descriptions.Item><Descriptions.Item label="HTTT ID">{profile.information_system_id}</Descriptions.Item>
    </Descriptions>
    <Row gutter={[16,16]}>
      <Col xs={24} md={8}><Card title="Compliance"><Progress percent={data.score?.overall_score || data.summary?.overall || 0} /><JsonView data={data.score} /></Card></Col>
      <Col xs={24} md={8}><Card title="Risk"><Descriptions size="small" column={1}><Descriptions.Item label="Mức"><StatusTag value={data.risk?.risk_level} /></Descriptions.Item><Descriptions.Item label="Điểm">{data.risk?.risk_score}</Descriptions.Item></Descriptions></Card></Col>
      <Col xs={24} md={8}><Card title="Readiness"><Progress percent={data.readiness?.readiness_score || 0} /><Alert type={data.readiness?.is_ready_for_assessment ? 'success' : 'warning'} message={data.readiness?.readiness_status || 'Chưa đánh giá'} /></Card></Col>
    </Row>
    <Tabs items={[
      { key: 'checklist', label: 'Checklist', children: <Card title="Checklist ATTT" extra={<Space><Button onClick={generateChecklist}>Sinh checklist</Button><Button type="primary" onClick={runAssessment}>Chạy assessment</Button></Space>}><Table loading={loading} rowKey="id" dataSource={data.checklist || []} columns={checklistColumns} scroll={{x:1200}} /></Card> },
      { key: 'evidence', label: 'Minh chứng', children: <Card title="Tài liệu minh chứng"><Form form={uploadForm} layout="inline" onFinish={uploadEvidence} style={{ marginBottom: 16 }}><Form.Item name="document_type" initialValue="OTHER"><Select style={{width:170}} options={['QUY_CHE_ATTT','SO_DO_MANG','PHUONG_AN_SAO_LUU','BIEN_BAN_DANH_GIA','OTHER'].map(v=>({value:v,label:v}))} /></Form.Item><Form.Item name="title"><Input placeholder="Tiêu đề" /></Form.Item><Form.Item name="checklist_answer_id"><InputNumber placeholder="Answer ID" /></Form.Item><Form.Item name="file" rules={[{required:true}]}><Upload beforeUpload={() => false} maxCount={1}><Button icon={<UploadOutlined />}>Chọn file</Button></Upload></Form.Item><Button htmlType="submit" type="primary">Upload</Button></Form><Table rowKey="id" dataSource={data.evidence || []} columns={[{title:'Tiêu đề',dataIndex:'title'},{title:'Loại',dataIndex:'document_type'},{title:'File',dataIndex:'original_filename'},{title:'Version',dataIndex:'version'},{title:'Tải',render:(_,r)=><Button size="small" onClick={() => download(`/evidence-documents/${r.id}/download`, r.original_filename)}>Download</Button>}]} /></Card> },
      { key: 'workflow', label: 'Workflow', children: <Card title="Luồng xử lý" extra={<Space wrap>{(data.workflow?.allowed_actions || []).map(a => <Button key={a} type="primary" onClick={() => transition(a)}>{a}</Button>)}</Space>}><Timeline items={(data.history || []).map(h => ({ children: `${h.created_at} - ${h.from_status || ''} → ${h.to_status} (${h.action}) ${h.comment || ''}` }))} /><Form form={commentForm} layout="inline" onFinish={addComment}><Form.Item name="comment" rules={[{required:true}]} style={{ flex: 1 }}><Input placeholder="Nhập ý kiến rà soát/phê duyệt" /></Form.Item><Button htmlType="submit">Thêm ý kiến</Button></Form><Table rowKey="id" dataSource={data.comments || []} columns={[{title:'Thời gian',dataIndex:'created_at'},{title:'Trạng thái',dataIndex:'workflow_state'},{title:'Ý kiến',dataIndex:'comment'}]} /></Card> },
      { key: 'export', label: 'Xuất hồ sơ', children: <Card title="Sinh biểu mẫu"><Space wrap><Button onClick={() => exportDoc('PROFILE_EXPLANATION', true)}>Thuyết minh hồ sơ</Button><Button onClick={() => exportDoc('SUBMISSION_REPORT', true)}>Tờ trình</Button><Button onClick={() => exportDoc('APPROVAL_DECISION', true)}>Quyết định</Button><Button onClick={() => exportDoc('CHECKLIST_APPENDIX')}>Phụ lục checklist</Button></Space></Card> },
      { key: 'review', label: 'Rà soát định kỳ', children: <Card title="Rà soát định kỳ" extra={<Button onClick={generateReview}>Tạo lịch rà soát 12 tháng</Button>}><Table rowKey="id" dataSource={data.reviews?.items || []} columns={[{title:'Mã',dataIndex:'review_code'},{title:'Loại',dataIndex:'review_type'},{title:'Trạng thái',dataIndex:'status',render:v=><StatusTag value={v}/>},{title:'Hạn',dataIndex:'due_date'},{title:'Findings',dataIndex:'findings'}]} /></Card> },
      { key: 'gap', label: 'Gap Analysis', children: <JsonView data={data.gap} title="Kết quả phân tích GAP" /> }
    ]} />
  </Space>;
}
