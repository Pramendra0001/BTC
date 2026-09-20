import test from 'node:test';
import assert from 'node:assert/strict';

// Mock localStorage
class LocalStorageMock {
  private store: Record<string, string> = {};
  getItem(key: string): string | null {
    return this.store[key] || null;
  }
  setItem(key: string, value: string): void {
    this.store[key] = value;
  }
  removeItem(key: string): void {
    delete this.store[key];
  }
  clear(): void {
    this.store = {};
  }
}

// Emulate hardened login handler logic from LoginPage.tsx
async function executeLogin(
  apiClient: { post: (url: string, data: any) => Promise<any> },
  credentials: { username: string; password: string },
  localStorageMock: LocalStorageMock,
  navigateSpy: (path: string) => void,
  setErrorMsg: (msg: string | null) => void
) {
  try {
    const res = await apiClient.post('/api/auth/login', {
      username: credentials.username.trim(),
      password: credentials.password,
    });

    if (res.data?.access_token) {
      localStorageMock.setItem('token', res.data.access_token);
      navigateSpy('/');
    } else {
      setErrorMsg('Authentication server did not return a valid session token.');
    }
  } catch (err: any) {
    setErrorMsg(err.response?.data?.detail || 'Invalid username or password credentials');
  }
}

// Emulate hardened register handler logic from LoginPage.tsx
async function executeRegister(
  apiClient: { post: (url: string, data: any) => Promise<any> },
  data: { username: string; email: string; password: string; confirmPassword: string },
  callbacks: {
    setMode: (mode: 'login' | 'register') => void;
    setLoginUsername: (username: string) => void;
    setSuccessMsg: (msg: string | null) => void;
    setErrorMsg: (msg: string | null) => void;
  }
) {
  const trimmedUsername = data.username.trim();
  const trimmedEmail = data.email.trim();

  if (trimmedUsername.length < 3) {
    callbacks.setErrorMsg('Username must be at least 3 characters long.');
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmedEmail)) {
    callbacks.setErrorMsg('Please enter a valid email address.');
    return;
  }

  if (data.password.length < 8) {
    callbacks.setErrorMsg('Password must be at least 8 characters long.');
    return;
  }

  if (data.password !== data.confirmPassword) {
    callbacks.setErrorMsg('Passwords do not match.');
    return;
  }

  try {
    await apiClient.post('/api/auth/register', {
      username: trimmedUsername,
      email: trimmedEmail,
      password: data.password,
    });

    callbacks.setLoginUsername(trimmedUsername);
    callbacks.setSuccessMsg('Account created successfully! Please log in with your credentials.');
    callbacks.setMode('login');
  } catch (err: any) {
    if (err.response?.status === 409) {
      callbacks.setErrorMsg(err.response?.data?.detail || 'Username or email address is already registered.');
    } else if (err.response?.data?.detail) {
      callbacks.setErrorMsg(String(err.response.data.detail));
    } else {
      callbacks.setErrorMsg('Registration failed. Please verify your details and try again.');
    }
  }
}

test('failed login does not create a token and does not navigate to dashboard', async () => {
  const storage = new LocalStorageMock();
  let navigatedPath: string | null = null;
  let error: string | null = null;

  const mockApi = {
    post: async () => {
      const err: any = new Error('Unauthorized');
      err.response = { status: 401, data: { detail: 'Incorrect username or password' } };
      throw err;
    },
  };

  await executeLogin(
    mockApi,
    { username: 'admin', password: 'wrongpassword' },
    storage,
    (path) => { navigatedPath = path; },
    (msg) => { error = msg; }
  );

  assert.equal(storage.getItem('token'), null, 'Token must NOT be created on failed login');
  assert.equal(navigatedPath, null, 'Must NOT navigate on failed login');
  assert.equal(error, 'Incorrect username or password');
});

test('successful login stores the real API token and navigates to dashboard', async () => {
  const storage = new LocalStorageMock();
  let navigatedPath: string | null = null;
  let error: string | null = null;

  const realToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.real.payload';
  const mockApi = {
    post: async () => ({
      data: { access_token: realToken, token_type: 'bearer' },
    }),
  };

  await executeLogin(
    mockApi,
    { username: 'validuser', password: 'correctpassword' },
    storage,
    (path) => { navigatedPath = path; },
    (msg) => { error = msg; }
  );

  assert.equal(storage.getItem('token'), realToken, 'Must store the real API token');
  assert.notEqual(storage.getItem('token'), 'demo-token');
  assert.notEqual(storage.getItem('token'), 'offline-demo-token');
  assert.equal(navigatedPath, '/');
  assert.equal(error, null);
});

test('registration still works and success switches to login', async () => {
  let registeredPayload: any = null;
  let currentMode: 'login' | 'register' = 'register';
  let loginUser = '';
  let successMsg: string | null = null;
  let errorMsg: string | null = null;

  const mockApi = {
    post: async (_url: string, data: any) => {
      registeredPayload = data;
      return { status: 201, data: { id: 10, username: data.username, role: 'VIEWER' } };
    },
  };

  await executeRegister(
    mockApi,
    {
      username: 'investigator_test',
      email: 'investigator@example.com',
      password: 'strong-password-123',
      confirmPassword: 'strong-password-123',
    },
    {
      setMode: (m) => { currentMode = m; },
      setLoginUsername: (u) => { loginUser = u; },
      setSuccessMsg: (s) => { successMsg = s; },
      setErrorMsg: (e) => { errorMsg = e; },
    }
  );

  assert.deepEqual(registeredPayload, {
    username: 'investigator_test',
    email: 'investigator@example.com',
    password: 'strong-password-123',
  });
  assert.equal(currentMode, 'login', 'Must switch mode to login upon registration success');
  assert.equal(loginUser, 'investigator_test', 'Must prefill login username');
  assert.equal(errorMsg, null);
  assert.match(successMsg || '', /Account created successfully/);
});

test('duplicate registration displays useful 409 conflict error', async () => {
  let currentMode: 'login' | 'register' = 'register';
  let errorMsg: string | null = null;

  const mockApi = {
    post: async () => {
      const err: any = new Error('Conflict');
      err.response = { status: 409, data: { detail: 'Username already registered' } };
      throw err;
    },
  };

  await executeRegister(
    mockApi,
    {
      username: 'existing_user',
      email: 'existing@example.com',
      password: 'strong-password-123',
      confirmPassword: 'strong-password-123',
    },
    {
      setMode: (m) => { currentMode = m; },
      setLoginUsername: () => {},
      setSuccessMsg: () => {},
      setErrorMsg: (e) => { errorMsg = e; },
    }
  );

  assert.equal(currentMode, 'register', 'Must remain in register mode on error');
  assert.equal(errorMsg, 'Username already registered', 'Must display useful conflict error message');
});
