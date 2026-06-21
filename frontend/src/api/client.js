const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export function getToken() { return localStorage.getItem('lpm_token'); }
export function setToken(token) { localStorage.setItem('lpm_token', token); }
export function clearToken() { localStorage.removeItem('lpm_token'); }

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';
  if (response.status === 204) return null;
  if (contentType.includes('application/json')) return response.json();
  return response.text();
}

export async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  const data = await parseResponse(response);
  if (!response.ok) {
    const message = typeof data === 'string' ? data : data?.detail || data?.message || `HTTP ${response.status}`;
    throw new Error(message);
  }
  return data;
}

export async function login(username, password) {
  const body = new URLSearchParams();
  body.append('username', username);
  body.append('password', password);
  const data = await fetch(`${API_BASE_URL}/auth/login`, { method: 'POST', body }).then(async (res) => {
    const payload = await parseResponse(res);
    if (!res.ok) throw new Error(typeof payload === 'string' ? payload : payload?.detail || 'Đăng nhập thất bại');
    return payload;
  });
  setToken(data.access_token);
  return data;
}

export function downloadUrl(path) { return `${API_BASE_URL}${path}`; }

function page(path, params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') search.append(k, v); });
  return request(`${path}${search.toString() ? `?${search}` : ''}`);
}

export const api = {
  me: () => request('/auth/me'),
  roles: (params) => page('/roles', params),
  createRole: (payload) => request('/roles', { method: 'POST', body: JSON.stringify(payload) }),
  updateRole: (id, payload) => request(`/roles/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteRole: (id) => request(`/roles/${id}`, { method: 'DELETE' }),
  identityProviderStatus: () => request('/auth/identity-provider/status'),

  users: (params) => page('/users', params),
  createUser: (payload) => request('/users', { method: 'POST', body: JSON.stringify(payload) }),
  updateUser: (id, payload) => request(`/users/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteUser: (id) => request(`/users/${id}`, { method: 'DELETE' }),
  lockUser: (id) => request(`/users/${id}/lock`, { method: 'POST' }),
  unlockUser: (id) => request(`/users/${id}/unlock`, { method: 'POST' }),
  resetUserPassword: (id, payload) => request(`/users/${id}/reset-password`, { method: 'POST', body: JSON.stringify(payload) }),

  identityProductionReadiness: () => request('/identity-provider/production-readiness'),
  ldapTestConnection: (payload) => request('/identity-provider/ldap/test-connection', { method: 'POST', body: JSON.stringify(payload || {}) }),
  ldapPreviewUser: (payload) => request('/identity-provider/ldap/preview-user', { method: 'POST', body: JSON.stringify(payload) }),
  ldapSyncUser: (payload) => request('/identity-provider/ldap/sync-user', { method: 'POST', body: JSON.stringify(payload) }),
  ssoAssertionDryRun: (payload) => request('/identity-provider/sso/assertion-dry-run', { method: 'POST', body: JSON.stringify(payload) }),
  ssoLoginHint: () => request('/auth/sso/login-hint'),
  changePassword: (payload) => request('/auth/change-password', { method: 'POST', body: JSON.stringify(payload) }),

  dashboardSummary: () => request('/dashboard/summary'),
  workflowSummary: () => request('/dashboard/workflow-summary'),
  complianceOverview: () => request('/dashboard/compliance-overview'),
  complianceDashboard: () => request('/dashboard/compliance'),
  evidenceGaps: () => request('/dashboard/evidence-gaps'),
  enterpriseOverview: () => request('/dashboard/enterprise/overview'),
  enterpriseLevelMatrix: () => request('/dashboard/enterprise/level-matrix'),
  enterpriseComplianceRisk: () => request('/dashboard/enterprise/compliance-risk'),
  enterpriseActionBoard: () => request('/dashboard/enterprise/action-board'),
  enterpriseReport: () => request('/dashboard/enterprise/executive-report'),
  periodicReviewDashboard: () => request('/dashboard/periodic-reviews'),

  organizations: (params) => page('/organizations', params),
  organizationTree: () => request('/organizations/tree'),
  organizationScopeSummary: (id) => request(`/organizations/${id}/scope-summary`),
  createOrganization: (payload) => request('/organizations', { method: 'POST', body: JSON.stringify(payload) }),
  updateOrganization: (id, payload) => request(`/organizations/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteOrganization: (id) => request(`/organizations/${id}`, { method: 'DELETE' }),

  systems: (params) => page('/information-systems', params),
  system: (id) => request(`/information-systems/${id}`),
  createSystem: (payload) => request('/information-systems', { method: 'POST', body: JSON.stringify(payload) }),
  updateSystem: (id, payload) => request(`/information-systems/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteSystem: (id) => request(`/information-systems/${id}`, { method: 'DELETE' }),

  profiles: (params) => page('/level-profiles', params),
  profile: (id) => request(`/level-profiles/${id}`),
  createProfile: (payload) => request('/level-profiles', { method: 'POST', body: JSON.stringify(payload) }),
  updateProfile: (id, payload) => request(`/level-profiles/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteProfile: (id) => request(`/level-profiles/${id}`, { method: 'DELETE' }),

  securityRequirements: (params) => page('/security-requirements', params),
  requirementsByLevel: (level) => request(`/security-requirements/by-level/${level}`),
  generateChecklist: (profileId) => request(`/profiles/${profileId}/generate-checklist`, { method: 'POST' }),
  checklist: (profileId) => request(`/profiles/${profileId}/checklist`),
  updateChecklistAnswer: (id, payload) => request(`/checklist-answers/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  profileComplianceSummary: (profileId) => request(`/profiles/${profileId}/compliance-summary`),

  classifyLevel: (payload) => request('/compliance/classify-level', { method: 'POST', body: JSON.stringify(payload) }),
  suggestLevel: (profileId) => request(`/profiles/${profileId}/compliance/suggest-level`),
  gapAnalysis: (profileId) => request(`/profiles/${profileId}/compliance/gap-analysis`),
  complianceScore: (profileId) => request(`/profiles/${profileId}/compliance/score`),
  risk: (profileId) => request(`/profiles/${profileId}/compliance/risk`),
  readiness: (profileId) => request(`/profiles/${profileId}/compliance/readiness`),
  runAssessment: (profileId) => request(`/profiles/${profileId}/compliance/run-assessment`, { method: 'POST' }),
  assessments: (profileId) => request(`/profiles/${profileId}/compliance/assessments`),

  evidenceDocuments: (params) => page('/evidence-documents', params),
  profileEvidence: (profileId) => request(`/profiles/${profileId}/evidence-documents`),
  uploadEvidence: (formData) => request('/evidence-documents', { method: 'POST', body: formData }),
  updateEvidence: (id, payload) => request(`/evidence-documents/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteEvidence: (id) => request(`/evidence-documents/${id}`, { method: 'DELETE' }),

  workflow: (profileId) => request(`/profiles/${profileId}/workflow`),
  transitionWorkflow: (profileId, payload) => request(`/profiles/${profileId}/workflow/transition`, { method: 'POST', body: JSON.stringify(payload) }),
  workflowHistory: (profileId) => request(`/profiles/${profileId}/workflow/history`),
  comments: (profileId) => request(`/profiles/${profileId}/comments`),
  addComment: (profileId, payload) => request(`/profiles/${profileId}/comments`, { method: 'POST', body: JSON.stringify(payload) }),

  exportedDocuments: (params) => page('/exported-documents', params),
  exportProfile: (profileId, payload) => request(`/profiles/${profileId}/exports`, { method: 'POST', body: JSON.stringify(payload) }),
  generateGovernmentDocument: (profileId, payload) => request(`/profiles/${profileId}/government-documents/generate`, { method: 'POST', body: JSON.stringify(payload) }),
  documentTemplates: (params) => page('/document-templates', params),
  templateCenterSummary: () => request('/document-templates/center/summary'),
  templateVariables: () => request('/document-templates/variables'),
  createDocumentTemplate: (payload) => request('/document-templates', { method: 'POST', body: JSON.stringify(payload) }),
  updateDocumentTemplate: (id, payload) => request(`/document-templates/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  activateDocumentTemplate: (id) => request(`/document-templates/${id}/activate`, { method: 'POST' }),
  deactivateDocumentTemplate: (id) => request(`/document-templates/${id}/deactivate`, { method: 'POST' }),
  uploadDocumentTemplate: (id, formData) => request(`/document-templates/${id}/upload`, { method: 'POST', body: formData }),
  previewTemplateContext: (payload) => request('/document-templates/preview-context', { method: 'POST', body: JSON.stringify(payload) }),
  governmentDocumentTypes: () => request('/government-documents/types'),

  notifications: (params) => page('/notifications', params),
  notificationSummary: () => request('/notifications/summary'),
  notificationRuntimeStatus: () => request('/notifications/runtime-status'),
  sendTestNotification: (payload) => request('/notifications/send-test', { method: 'POST', body: JSON.stringify(payload) }),
  sendEmailTest: (payload) => request('/notifications/send-email-test', { method: 'POST', body: JSON.stringify(payload) }),
  sendTelegramTest: (payload) => request('/notifications/send-telegram-test', { method: 'POST', body: JSON.stringify(payload) }),
  sendDueReviewReminders: () => request('/notifications/send-due-review-reminders', { method: 'POST' }),

  periodicReviewsDueSoon: () => request('/periodic-reviews/due-soon'),
  profilePeriodicReviews: (profileId, params) => page(`/profiles/${profileId}/periodic-reviews`, params),
  generateNextReview: (profileId, payload) => request(`/profiles/${profileId}/periodic-reviews/generate-next`, { method: 'POST', body: JSON.stringify(payload || {}) }),
  completeReview: (reviewId, payload) => request(`/periodic-reviews/${reviewId}/complete`, { method: 'POST', body: JSON.stringify(payload || {}) }),

  auditLogs: (params) => page('/audit-logs', params),
  auditSummary: () => request('/audit-logs/summary'),
  auditActions: () => request('/audit-logs/actions'),

  users: (params) => page('/users', params),
  securitySummary: () => request('/security/summary'),
  securityEvents: () => request('/security/events'),
  releaseInfo: () => request('/release/info'),
  releaseReadiness: () => request('/release/readiness'),
  productionReadiness: () => request('/release/production-readiness'),
  uatChecklist: () => request('/release/uat-checklist'),
  dataFootprint: () => request('/release/data-footprint'),


  dossierSummary: (profileId) => request(`/profiles/${profileId}/dossier/summary`),
  profileVersions: (profileId, params) => page(`/profiles/${profileId}/versions`, params),
  createProfileVersion: (profileId, payload) => request(`/profiles/${profileId}/versions`, { method: 'POST', body: JSON.stringify(payload || {}) }),
  profileVersion: (versionId) => request(`/profile-versions/${versionId}`),
  compareProfileVersions: (fromVersionId, toVersionId) => request(`/profile-versions/compare?from_version_id=${fromVersionId}&to_version_id=${toVersionId}`),
  signProfileVersion: (versionId, payload) => request(`/profile-versions/${versionId}/sign`, { method: 'POST', body: JSON.stringify(payload || {}) }),
  profileSignatures: (profileId, params) => page(`/profiles/${profileId}/signatures`, params),
  runtime: () => request('/system/runtime'),
  productionChecklist: () => request('/system/production-checklist'),

  riskRegisters: (params) => page('/risk-registers', params),
  riskRegisterSummary: () => request('/risk-registers/summary'),
  createRiskRegister: (payload) => request('/risk-registers', { method: 'POST', body: JSON.stringify(payload) }),
  updateRiskRegister: (id, payload) => request(`/risk-registers/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  closeRiskRegister: (id) => request(`/risk-registers/${id}/close`, { method: 'POST' }),
  slaPolicies: (params) => page('/sla/policies', params),
  createSlaPolicy: (payload) => request('/sla/policies', { method: 'POST', body: JSON.stringify(payload) }),
  seedSlaPolicies: () => request('/sla/policies/seed-defaults', { method: 'POST' }),
  slaSummary: () => request('/sla/summary'),

  assessmentPortalSummary: () => request('/assessment-portal/summary'),
  assessmentCases: (params) => page('/assessment-cases', params),
  createAssessmentCase: (payload) => request('/assessment-cases', { method: 'POST', body: JSON.stringify(payload) }),
  updateAssessmentCase: (id, payload) => request(`/assessment-cases/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  submitAssessmentCase: (id) => request(`/assessment-cases/${id}/submit`, { method: 'POST' }),
  completeAssessmentCase: (id) => request(`/assessment-cases/${id}/complete`, { method: 'POST' }),
  executiveKpis: () => request('/dashboard/executive/kpis'),
  executivePortfolio: () => request('/dashboard/executive/portfolio'),
  executivePriorityActions: () => request('/dashboard/executive/priority-actions'),
  executiveBoardPack: () => request('/dashboard/executive/board-pack'),

  aiClassifyLevel: (payload) => request('/ai/classify-level', { method: 'POST', body: JSON.stringify(payload) }),
  aiRecommendProfile: (profileId) => request(`/profiles/${profileId}/ai/recommend-level`, { method: 'POST' }),
  aiRecommendationHistory: (profileId) => request(`/profiles/${profileId}/ai/recommendations`),
  aiClassificationDashboard: () => request('/dashboard/ai-classification'),
  aiMisclassifiedProfiles: () => request('/dashboard/ai-classification/misclassified'),
  signatureGatewayStatus: () => request('/signature-gateway/status'),
  seedSignatureProviders: () => request('/signature-providers/seed-defaults', { method: 'POST' }),
  signatureProviders: (params) => page('/signature-providers', params),
  createSignatureProvider: (payload) => request('/signature-providers', { method: 'POST', body: JSON.stringify(payload) }),
  updateSignatureProvider: (id, payload) => request(`/signature-providers/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  createRealSignRequest: (versionId, payload) => request(`/profile-versions/${versionId}/real-sign-requests`, { method: 'POST', body: JSON.stringify(payload || {}) }),
  signatureRequests: (params) => page('/signature-requests', params),
  simulateSignatureCallback: (requestCode) => request(`/signature-requests/${requestCode}/simulate-callback`, { method: 'POST' }),


  assessmentWorkflowSummary: () => request('/assessment-workflow/summary'),
  assessmentWorkflowRules: () => request('/assessment-workflow/rules'),
  assessmentWorkflowEvents: (caseId) => request(`/assessment-cases/${caseId}/workflow-events`),
  transitionAssessmentWorkflow: (caseId, payload) => request(`/assessment-cases/${caseId}/workflow-transition`, { method: 'POST', body: JSON.stringify(payload || {}) }),

  cmdbDashboard: () => request('/cmdb/dashboard'),
  cmdbAssets: (params) => page('/cmdb-assets', params),
  createCmdbAsset: (payload) => request('/cmdb-assets', { method: 'POST', body: JSON.stringify(payload) }),
  updateCmdbAsset: (id, payload) => request(`/cmdb-assets/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteCmdbAsset: (id) => request(`/cmdb-assets/${id}`, { method: 'DELETE' }),
  cmdbApplications: (params) => page('/cmdb-applications', params),
  createCmdbApplication: (payload) => request('/cmdb-applications', { method: 'POST', body: JSON.stringify(payload) }),
  updateCmdbApplication: (id, payload) => request(`/cmdb-applications/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteCmdbApplication: (id) => request(`/cmdb-applications/${id}`, { method: 'DELETE' }),
  cmdbDatabases: (params) => page('/cmdb-databases', params),
  createCmdbDatabase: (payload) => request('/cmdb-databases', { method: 'POST', body: JSON.stringify(payload) }),
  updateCmdbDatabase: (id, payload) => request(`/cmdb-databases/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteCmdbDatabase: (id) => request(`/cmdb-databases/${id}`, { method: 'DELETE' }),
  cmdbNetworkDevices: (params) => page('/cmdb-network-devices', params),
  createCmdbNetworkDevice: (payload) => request('/cmdb-network-devices', { method: 'POST', body: JSON.stringify(payload) }),
  updateCmdbNetworkDevice: (id, payload) => request(`/cmdb-network-devices/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteCmdbNetworkDevice: (id) => request(`/cmdb-network-devices/${id}`, { method: 'DELETE' }),
  cmdbImportAssets: (payload) => request('/cmdb/import/assets', { method: 'POST', body: JSON.stringify(payload) }),
  cmdbProfileInventory: (profileId) => request(`/profiles/${profileId}/cmdb-inventory`),
  cmdbSyncProfile: (profileId) => request(`/profiles/${profileId}/cmdb-sync`, { method: 'POST' }),


  siemStatus: () => request('/siem/status'),
  siemDashboard: () => request('/dashboard/siem'),
  siemCorrelationSummary: () => request('/siem/correlation/summary'),
  seedSiemConnectors: () => request('/siem/connectors/seed-defaults', { method: 'POST' }),
  seedSiemRules: () => request('/siem/rules/seed-defaults', { method: 'POST' }),
  siemConnectors: (params) => page('/siem/connectors', params),
  createSiemConnector: (payload) => request('/siem/connectors', { method: 'POST', body: JSON.stringify(payload) }),
  siemEvents: (params) => page('/siem/events', params),
  ingestSiemEvent: (payload) => request('/siem/events/ingest', { method: 'POST', body: JSON.stringify(payload) }),
  ingestAuditToSiem: () => request('/siem/events/ingest-audit', { method: 'POST' }),
  ingestSecurityToSiem: () => request('/siem/events/ingest-security', { method: 'POST' }),
  siemRules: (params) => page('/siem/rules', params),
  createSiemRule: (payload) => request('/siem/rules', { method: 'POST', body: JSON.stringify(payload) }),


  complianceAutomationDashboard: () => request('/dashboard/compliance-automation'),
  seedComplianceAutomationRules: () => request('/compliance-automation/rules/seed-defaults', { method: 'POST' }),
  complianceAutomationRules: (params) => page('/compliance-automation/rules', params),
  runComplianceAutomation: (payload) => request('/compliance-automation/run', { method: 'POST', body: JSON.stringify(payload || {}) }),
  complianceAutomationRuns: (params) => page('/compliance-automation/runs', params),
  complianceAutomationFindings: (params) => page('/compliance-automation/findings', params),

  complianceMonitoringDashboard: () => request('/dashboard/compliance-monitoring'),
  complianceMonitoringScore: (profileId) => request(`/compliance-monitoring/score/${profileId}`),
  runComplianceMonitoring: (payload) => request('/compliance-monitoring/recalculate', { method: 'POST', body: JSON.stringify(payload || {}) }),
  complianceMonitoringSnapshots: (params) => page('/compliance-monitoring/snapshots', params),
  complianceMonitoringFindings: (params) => page('/compliance-monitoring/findings', params),
  complianceMonitoringNotifications: (params) => page('/compliance-monitoring/notifications', params),
  complianceMonitoringHeatmap: () => request('/compliance-monitoring/heatmap'),
  complianceMonitoringTrends: (profileId, limit = 30) => request(`/compliance-monitoring/trends/${profileId}?limit=${limit}`),

  assessmentFeedbacks: (params) => page('/assessment-feedbacks', params),
  createAssessmentFeedback: (payload) => request('/assessment-feedbacks', { method: 'POST', body: JSON.stringify(payload) }),
  updateAssessmentFeedback: (id, payload) => request(`/assessment-feedbacks/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  respondAssessmentFeedback: (id, payload) => request(`/assessment-feedbacks/${id}/respond`, { method: 'POST', body: JSON.stringify(payload) }),

  enterpriseReportingDashboard: () => request('/dashboard/enterprise-reporting'),
  enterpriseReportingSummary: () => request('/enterprise-reporting/summary'),
  generateEnterpriseReportSnapshot: (payload) => request('/enterprise-reporting/snapshots/generate', { method: 'POST', body: JSON.stringify(payload || {}) }),
  enterpriseReportSnapshots: (params) => page('/enterprise-reporting/snapshots', params),
  enterpriseDataWarehouseMetrics: (params) => page('/enterprise-reporting/data-warehouse/metrics', params),
  enterprisePortfolioCsvUrl: () => downloadUrl('/enterprise-reporting/export/portfolio-csv'),

  enterpriseCenterDashboard: () => request('/enterprise-center/dashboard'),
  enterpriseSeedDefaults: () => request('/enterprise-center/seed-defaults', { method: 'POST' }),
  enterpriseReadiness: () => request('/enterprise-center/readiness'),
  enterpriseHealth: () => request('/enterprise-center/health'),
  enterpriseConfigurations: (params) => page('/enterprise-center/configurations', params),
  enterpriseJobs: (params) => page('/enterprise-center/jobs', params),
  enterpriseRetentionPolicies: (params) => page('/enterprise-center/retention-policies', params),
  enterpriseBackups: (params) => page('/enterprise-center/backups', params),
  enterpriseCreateMockBackup: (payload) => request('/enterprise-center/backups/mock', { method: 'POST', body: JSON.stringify(payload) }),
  enterpriseValidateBackup: (id) => request(`/enterprise-center/backups/${id}/validate`, { method: 'POST' }),

};
