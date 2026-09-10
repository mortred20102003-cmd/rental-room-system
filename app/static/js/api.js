const api = {
  getToken() {
    return localStorage.getItem('jwt_token');
  },

  normalizePath(path) {
    if (!path || typeof path !== 'string') return path;
    if (path.startsWith('/api/v1') || path.startsWith('/system/')) {
      return path;
    }
    return `/api/v1${path.startsWith('/') ? path : `/${path}`}`;
  },

  async request(path, options = {}) {
    const safePath = this.normalizePath(path);
    const token = this.getToken();
    const headers = new Headers(options.headers || {});

    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(safePath, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      localStorage.removeItem('jwt_token');
      window.location.href = '/login';
      throw new Error('Session expired. Please sign in again.');
    }

    if (!response.ok) {
      let message = 'Request failed';
      try {
        const payload = await response.json();
        message = payload.detail || payload.message || message;
      } catch (error) {
        // ignore JSON parse errors
      }
      throw new Error(message);
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return response.json();
    }

    return response.text();
  },

  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    return data.access_token;
  },

  async get(path) {
    return this.request(path, { method: 'GET' });
  },

  async post(path, body) {
    return this.request(path, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  },

  async put(path, body) {
    return this.request(path, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },

  async del(path) {
    return this.request(path, { method: 'DELETE' });
  },
};
