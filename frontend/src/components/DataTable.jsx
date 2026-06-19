import { Alert, Card, Input, Space, Table } from 'antd';
import React, { useMemo, useState } from 'react';

export default function DataTable({ title, data, columns, rowKey = 'id', loading, error, extra, searchable = true }) {
  const [q, setQ] = useState('');
  const rows = Array.isArray(data) ? data : data?.items || [];
  const filtered = useMemo(() => {
    if (!q) return rows;
    const needle = q.toLowerCase();
    return rows.filter((r) => JSON.stringify(r || {}).toLowerCase().includes(needle));
  }, [rows, q]);
  return (
    <Card title={title} extra={extra}>
      {error && <Alert type="error" showIcon message="Lỗi tải dữ liệu" description={String(error)} style={{ marginBottom: 12 }} />}
      <Space style={{ marginBottom: 12 }}>
        {searchable && <Input.Search allowClear placeholder="Tìm kiếm nhanh trên dữ liệu đã tải" onSearch={setQ} onChange={(e) => setQ(e.target.value)} style={{ width: 360 }} />}
      </Space>
      <Table size="middle" rowKey={rowKey} dataSource={filtered} columns={columns} loading={loading} scroll={{ x: 900 }} />
    </Card>
  );
}
