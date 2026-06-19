import React from 'react';
import { Card, Table, Typography } from 'antd';

export function SystemsPage({ items }) {
  return (
    <Card>
      <Typography.Title level={3}>Danh mục hệ thống thông tin</Typography.Title>
      <Table rowKey="id" dataSource={items || []} columns={[
        { title: 'Mã', dataIndex: 'code' },
        { title: 'Tên hệ thống', dataIndex: 'name' },
        { title: 'Đơn vị chủ quản', dataIndex: 'owner_unit' },
        { title: 'Mô hình', dataIndex: 'deployment_model' },
        { title: 'Trạng thái', dataIndex: 'status' },
      ]} />
    </Card>
  );
}

export function ProfilesPage({ items }) {
  return (
    <Card>
      <Typography.Title level={3}>Hồ sơ đề xuất cấp độ</Typography.Title>
      <Table rowKey="id" dataSource={items || []} columns={[
        { title: 'Tên hồ sơ', dataIndex: 'profile_name' },
        { title: 'Cấp độ', dataIndex: 'proposed_level' },
        { title: 'Trạng thái', dataIndex: 'status' },
        { title: 'Ngày rà soát', dataIndex: 'review_due_date' },
      ]} />
    </Card>
  );
}

export function NotificationsPage({ items }) {
  return (
    <Card>
      <Typography.Title level={3}>Thông báo</Typography.Title>
      <Table rowKey="id" dataSource={items || []} columns={[
        { title: 'Loại', dataIndex: 'event_type' },
        { title: 'Kênh', dataIndex: 'channel' },
        { title: 'Người nhận', dataIndex: 'recipient' },
        { title: 'Tiêu đề', dataIndex: 'subject' },
        { title: 'Trạng thái', dataIndex: 'status' },
        { title: 'Thời gian', dataIndex: 'created_at' },
      ]} />
    </Card>
  );
}
