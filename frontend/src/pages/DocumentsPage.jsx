import { Button, Card, Select, Space, Table, message } from 'antd';
import React, { useEffect, useState } from 'react';
import PageHeader from '../components/PageHeader';
import StatusTag from '../components/StatusTag';
import { api, downloadFile } from '../api/client';

export default function DocumentsPage({ profiles }) {
  const [data,setData]=useState({evidence:[],exports:[],templates:[]}); const [profileId,setProfileId]=useState(profiles?.[0]?.id);
  const load=async()=>{ const [e,x,t]=await Promise.allSettled([api.evidenceDocuments({limit:100}),api.exportedDocuments({limit:100}),api.documentTemplates({limit:100})]); const val=(r)=>r.status==='fulfilled'?(r.value.items||r.value):[]; setData({evidence:val(e),exports:val(x),templates:val(t)}); };
  useEffect(()=>{load();},[]);
  const gen=async(type)=> { try { const doc = await api.generateGovernmentDocument(profileId,{document_type:type,file_format:'docx'}); message.success(`Đã sinh tài liệu: ${doc.filename || doc.original_filename || doc.document_type || type}`); load(); } catch(e) { message.error(e.message || 'Không sinh được tài liệu'); } };
  const download = async (path, filename) => { try { const res = await downloadFile(path, filename); message.success(`Đã tải: ${res.filename}`); } catch(e) { message.error(e.message || 'Không tải được tài liệu'); } };
  return <>
    <PageHeader title="Tài liệu, biểu mẫu và xuất hồ sơ" subtitle="Quản lý minh chứng, tài liệu đã xuất và template biểu mẫu cơ quan." actions={<Space><Select style={{width:260}} value={profileId} onChange={setProfileId} options={(profiles||[]).map(p=>({value:p.id,label:p.profile_code}))}/><Button onClick={()=>gen('PROFILE_EXPLANATION')}>Sinh thuyết minh</Button><Button onClick={()=>gen('SUBMISSION_REPORT')}>Sinh tờ trình</Button></Space>} />
    <Card title="Tài liệu minh chứng"><Table rowKey="id" dataSource={data.evidence} columns={[{title:'Tiêu đề',dataIndex:'title'},{title:'Loại',dataIndex:'document_type'},{title:'Hồ sơ',dataIndex:'profile_id'},{title:'File',dataIndex:'original_filename'},{title:'Dung lượng',dataIndex:'file_size'},{title:'Tải',render:(_,r)=><Button size="small" onClick={() => download(`/evidence-documents/${r.id}/download`, r.original_filename)}>Download</Button>}]} /></Card>
    <Card title="Tài liệu đã xuất" style={{marginTop:16}}><Table rowKey="id" dataSource={data.exports} columns={[{title:'Loại',dataIndex:'document_type'},{title:'Tên file',render:(_,r)=>r.filename || r.original_filename},{title:'Format',dataIndex:'file_format'},{title:'Trạng thái',dataIndex:'status',render:v=><StatusTag value={v}/>},{title:'Tải',render:(_,r)=><Button size="small" onClick={() => download(`/exported-documents/${r.id}/download`, r.original_filename || r.filename)}>Download</Button>}]} /></Card>
    <Card title="Template biểu mẫu" style={{marginTop:16}}><Table rowKey="id" dataSource={data.templates} columns={[{title:'Code',dataIndex:'code'},{title:'Tên',dataIndex:'name'},{title:'Loại',dataIndex:'document_type'},{title:'Phiên bản',dataIndex:'version'},{title:'Đơn vị',dataIndex:'agency_name'},{title:'Active',dataIndex:'is_active',render:v=>v?'Có':'Không'}]} /></Card>
  </>;
}
