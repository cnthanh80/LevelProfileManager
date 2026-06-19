import React from 'react';
import { Tag } from 'antd';

const colors = {
  DRAFT: 'default', INTERNAL_REVIEW: 'processing', REVISION_REQUIRED: 'warning', REVIEWED: 'cyan',
  LEADER_APPROVAL: 'geekblue', INTERNALLY_APPROVED: 'blue', SUBMITTED_FOR_ASSESSMENT: 'purple',
  ASSESSMENT_COMMENTED: 'orange', COMPLETED: 'green', APPROVAL_DECISION_ISSUED: 'green', REVIEW_DUE: 'red',
  COMPLIANT: 'green', NON_COMPLIANT: 'red', NOT_APPLICABLE: 'default', SENT: 'green', FAILED: 'red', PENDING: 'gold',
  active: 'green', inactive: 'default', production: 'blue', dr: 'purple', test: 'gold', cloud: 'cyan', hybrid: 'geekblue', on_premise: 'blue'
};

export default function StatusTag({ value }) {
  if (value === undefined || value === null || value === '') return <Tag>—</Tag>;
  return <Tag color={colors[value] || colors[String(value).toUpperCase()] || 'default'}>{String(value)}</Tag>;
}
