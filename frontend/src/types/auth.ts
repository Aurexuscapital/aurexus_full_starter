export interface User {
  id: number;
  email: string;
  role: 'public' | 'developer' | 'investor' | 'admin';
  first_name?: string;
  last_name?: string;
  company?: string;
  is_active: boolean;
  is_verified: boolean;
  total_questions_asked: number;
  last_login?: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  company?: string;
  phone?: string;
  role: 'public' | 'developer' | 'investor' | 'admin';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PublicQuestionLimit {
  questions_asked: number;
  questions_remaining: number;
  requires_signup: boolean;
}

