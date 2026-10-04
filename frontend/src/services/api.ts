const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') || 'http://localhost:8000';

export class ApiError extends Error {
  public status: number;
  public data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;

  let url = `${API_BASE_URL}/${endpoint.replace(/^\/+/, '')}`;

  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  const config: RequestInit = {
    ...customConfig,
    headers: {
      ...(customConfig.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(localStorage.getItem('token') ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : {}),
      ...headers,
    },
  };

  let response: Response;
  try {
    response = await fetch(url, config);
  } catch (error) {
    // Network errors (DNS, connection refused, CORS failure before preflight)
    throw new Error(`Network failure or CORS issue: ${error instanceof Error ? error.message : String(error)}`);
  }

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    let errorMessage = `API Error: ${response.status} ${response.statusText}`;
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as any).detail;
      errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
    }
    throw new ApiError(response.status, errorMessage, data);
  }

  return data as T;
}

export const apiClient = {
  get: <T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>) => 
    request<T>(endpoint, { ...options, method: 'GET' }),
    
  post: <T>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>) => 
    request<T>(endpoint, { ...options, method: 'POST', body: data ? (data instanceof FormData ? data : JSON.stringify(data)) : undefined }),
    
  put: <T>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>) => 
    request<T>(endpoint, { ...options, method: 'PUT', body: data ? (data instanceof FormData ? data : JSON.stringify(data)) : undefined }),
    
  patch: <T>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>) => 
    request<T>(endpoint, { ...options, method: 'PATCH', body: data ? (data instanceof FormData ? data : JSON.stringify(data)) : undefined }),
    
  delete: <T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>) => 
    request<T>(endpoint, { ...options, method: 'DELETE' }),
};
