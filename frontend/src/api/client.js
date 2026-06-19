const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export function getToken() {
  return localStorage.getItem('lpm_token');
}

export function setToken(token) {
  localStorage.setItem('lpm_token', token);
}

export function clearToken() {
  localStorage.removeItem('lpm_token');
}

async function request(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return response.json();
  return response.text();
}

export async function login(username, password) {
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);
  const data = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    body,
  }).then(async (res) => {
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  });
  setToken(data.access_token);
  return data;
}

export const api = {
  me: () => request('/auth/me'),
  dashboardSummary: () => request('/dashboard/summary'),
  workflowSummary: () => request('/dashboard/workflow-summary'),
  complianceOverview: () => request('/dashboard/compliance-overview'),
  evidenceGaps: () => request('/dashboard/evidence-gaps'),
  systems: () => request('/information-systems?limit=20'),
  profiles: () => request('/level-profiles?limit=20'),
  notifications: () => request('/notifications?limit=10'),
};
