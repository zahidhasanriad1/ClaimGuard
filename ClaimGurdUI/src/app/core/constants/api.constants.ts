import { environment } from '../../../environments/environment';

export const API_BASE_URL = environment.apiBaseUrl;
export const USE_MOCK_AUTH = environment.useMockAuth;
export const DEMO_EMAIL = environment.demoEmail;
export const DEMO_PASSWORD = environment.demoPassword;

export const STORAGE_KEYS = {
  accessToken: 'claimguard_access_token',
  currentUser: 'claimguard_current_user'
};
