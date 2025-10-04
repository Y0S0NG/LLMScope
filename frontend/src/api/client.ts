/**
 * API client
 */

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIClient {
  private baseUrl: string;
  private apiKey: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
  }

  private async request(
    method: string,
    path: string,
    data?: any
  ): Promise<any> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    const config: RequestInit = {
      method,
      headers,
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    const response = await fetch(`${this.baseUrl}${path}`, config);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async get(path: string): Promise<any> {
    return this.request('GET', path);
  }

  async post(path: string, data: any): Promise<any> {
    return this.request('POST', path, data);
  }

  async put(path: string, data: any): Promise<any> {
    return this.request('PUT', path, data);
  }

  async delete(path: string): Promise<any> {
    return this.request('DELETE', path);
  }
}

export const apiClient = new APIClient(BASE_URL);
