import { Card } from 'antd';
export default function JsonView({ data, title }) {
  return <Card size="small" title={title}><pre style={{ margin: 0, maxHeight: 420, overflow: 'auto' }}>{JSON.stringify(data || {}, null, 2)}</pre></Card>;
}
