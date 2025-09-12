import { User, LoginRequest, RegisterRequest, AuthResponse, PublicQuestionLimit } from '@/types/auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export class AuthService {
  private static tokenKey = 'aurexus_token';
  private static userKey = 'aurexus_user';

  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    this.setToken(data.access_token);
    this.setUser(data.user);
    return data;
  }

  static async register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  }

  static async getCurrentUser(): Promise<User | null> {
    const token = this.getToken();
    if (!token) return null;

    try {
      const response = await fetch(`${API_BASE}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        this.logout();
        return null;
      }

      const user = await response.json();
      this.setUser(user);
      return user;
    } catch {
      this.logout();
      return null;
    }
  }

  static async getPublicQuestionLimit(sessionId: string): Promise<PublicQuestionLimit> {
    const response = await fetch(`${API_BASE}/api/auth/public/question-limit/${sessionId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get question limit');
    }

    return response.json();
  }

  static setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.tokenKey, token);
    }
  }

  static getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(this.tokenKey);
    }
    return null;
  }

  static setUser(user: User): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.userKey, JSON.stringify(user));
    }
  }

  static getUser(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem(this.userKey);
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }

  static logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
    }
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }

  static hasRole(role: string): boolean {
    const user = this.getUser();
    return user?.role === role || user?.role === 'admin';
  }
}
