import React, { useEffect, useState } from 'react';
import { Alert, Card, Col, Progress, Row, Space, Table, Tag, Typography } from 'antd';
import PageHeader from '../components/PageHeader';
import JsonView from '../components/JsonView';
import { api } from '../api/client';

function statusColor(status) {
  if (status === 'PASS' || status === true || status === 'READY' || status === 'READY_FOR_PRODUCTION_PILOT') return 'green';
  if (status === 'WARN' || status === 'READY_WITH_WARNINGS' || status === 'READY_FOR_UAT') return 'orange';
  return 'red';
}

export default function ReleasePage() {
  const [data, setData] = useState({});

  useEffect(() => {
    Promise.allSettled([
      api.releaseInfo(),
      api.releaseReadiness(),
      api.productionReadiness(),
      api.uatChecklist(),
      api.dataFootprint(),
    ]).then((r) => {
      const v = (i, d) => (r[i].status === 'fulfilled' ? r[i].value : d);
      setData({ info: v(0, {}), readiness: v(1, {}), production: v(2, {}), uat: v(3, {}), footprint: v(4, {}) });
    });
  }, []);

  const readinessScore = Number(data.readiness?.readiness_score || 0);
  const uatItems = Array.isArray(data.uat?.checklist) ? data.uat.checklist : Array.isArray(data.uat) ? data.uat : [];
  const controls = Array.isArray(data.production?.controls) ? data.production.controls : [];

  return (
    <>
      <PageHeader title="Production Release v3.0" subtitle="Readiness, UAT checklist, production controls và data footprint." />
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message="Baseline sẵn sàng UAT/production pilot"
        description="Ký số đang ở chế độ mock. Trước go-live chính thức cần cấu hình JWT secret, SMTP/Telegram, LDAP/SSO và phương án backup/restore."
      />
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Readiness Score">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Progress percent={readinessScore} status={readinessScore >= 85 ? 'success' : 'active'} />
              <Typography.Text>Trạng thái: <Tag color={statusColor(data.readiness?.status)}>{data.readiness?.status || 'N/A'}</Tag></Typography.Text>
              <Typography.Text>Passed: {data.readiness?.passed || 0}/{data.readiness?.total || 0}</Typography.Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Production Status">
            <Space direction="vertical">
              <Tag color={statusColor(data.production?.status)}>{data.production?.status || 'N/A'}</Tag>
              <Typography.Text>Fails: {data.production?.fails ?? 0}</Typography.Text>
              <Typography.Text>Warnings: {data.production?.warnings ?? 0}</Typography.Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <JsonView title="Release Info" data={data.info} />
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Production Controls">
            <Table
              rowKey={(r) => `${r.group}-${r.item}`}
              dataSource={controls}
              columns={[
                { title: 'Nhóm', dataIndex: 'group', width: 120 },
                { title: 'Kiểm soát', dataIndex: 'item' },
                { title: 'Trạng thái', dataIndex: 'status', render: (v) => <Tag color={statusColor(v)}>{v}</Tag>, width: 120 },
                { title: 'Chi tiết', dataIndex: 'detail' },
              ]}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="UAT Checklist v3.0">
            <Table
              rowKey={(r) => r.code || r.name}
              dataSource={uatItems}
              columns={[
                { title: 'Mã', dataIndex: 'code', width: 90 },
                { title: 'Mục kiểm thử', dataIndex: 'name' },
                { title: 'Trạng thái', dataIndex: 'status', render: (v) => <Tag>{v || 'TODO'}</Tag>, width: 120 },
              ]}
              pagination={{ pageSize: 8 }}
              size="small"
            />
          </Card>
        </Col>
        <Col span={24}><JsonView title="Data Footprint" data={data.footprint} /></Col>
      </Row>
    </>
  );
}
