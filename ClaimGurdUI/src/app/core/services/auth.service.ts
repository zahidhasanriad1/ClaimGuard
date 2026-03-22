import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError, delay, tap } from 'rxjs';
import { Router } from '@angular/router';

import { API_BASE_URL, DEMO_EMAIL, DEMO_PASSWORD, STORAGE_KEYS, USE_MOCK_AUTH } from '../constants/api.constants';
import { CurrentUser, LoginRequest, LoginResponse } from '../models/auth.models';
import { StorageService } from './storage.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly storage = inject(StorageService);

  readonly currentUser = signal<CurrentUser | null>(this.storage.get<CurrentUser>(STORAGE_KEYS.currentUser));
  readonly isAuthenticated = signal<boolean>(!!this.storage.get<string>(STORAGE_KEYS.accessToken));

  login(payload: LoginRequest): Observable<LoginResponse> {
    if (USE_MOCK_AUTH) {
      if (payload.email !== DEMO_EMAIL || payload.password !== DEMO_PASSWORD) {
        return throwError(() => new Error('Invalid email or password'));
      }

      const mockResponse: LoginResponse = {
        access_token: 'mock_jwt_token_claimguard_demo',
        token_type: 'bearer',
        expires_in: 3600,
        user: {
          id: 1,
          email: DEMO_EMAIL,
          name: 'Admin User',
          role: 'admin'
        }
      };

      return of(mockResponse).pipe(
        delay(400),
        tap((response) => this.setSession(response))
      );
    }

    return this.http.post<LoginResponse>(`${API_BASE_URL}/auth/login`, payload).pipe(
      tap((response) => this.setSession(response))
    );
  }

  logout(): void {
    this.storage.clearMany([STORAGE_KEYS.accessToken, STORAGE_KEYS.currentUser]);
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
    this.router.navigate(['/login']);
  }

  getAccessToken(): string | null {
    return this.storage.get<string>(STORAGE_KEYS.accessToken);
  }

  private setSession(response: LoginResponse): void {
    this.storage.set(STORAGE_KEYS.accessToken, response.access_token);
    this.storage.set(STORAGE_KEYS.currentUser, response.user);
    this.currentUser.set(response.user);
    this.isAuthenticated.set(true);
  }
}
