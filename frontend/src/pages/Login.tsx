import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

import styles from './Login.module.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Create x-www-form-urlencoded data
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // We don't fetch user immediately, wait for context or fetch now
      // Actually we should fetch /me to get user details to pass to context
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });

      if (!userResponse.ok) {
        throw new Error('Failed to fetch user profile');
      }

      const userData = await userResponse.json();
      login(data.access_token, userData);
      navigate('/overview');
    } catch (err: any) {
      setError(err.message || 'An error occurred during login');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginCard}>
        <div className={styles.header}>
          <h1 className={styles.title}>National Material Master</h1>
          <p className={styles.subtitle}>AI-powered material harmonization across CPSEs</p>
        </div>

        <form onSubmit={handleLogin}>
          <div className={styles.formGroup}>
            <label className={styles.label}>Official ID / Email</label>
            <input 
              type="text" 
              className={styles.input} 
              placeholder="Enter your official ID" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Password</label>
            <input 
              type="password" 
              className={styles.input} 
              placeholder="Enter your password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>CPSE / Organization</label>
            <select className={styles.select} required defaultValue="">
              <option value="" disabled>Select your organization</option>
              <option value="iocl">IOCL - Indian Oil Corporation Limited</option>
              <option value="ntpc">NTPC Limited</option>
              <option value="bhel">BHEL - Bharat Heavy Electricals Limited</option>
              <option value="gail">GAIL (India) Limited</option>
              <option value="ministry">Ministry of Steel</option>
            </select>
          </div>
          
          <div className={styles.formGroup}>
            <label className={styles.label}>Role</label>
            <select className={styles.select} required defaultValue="admin">
              <option value="admin">Administrator</option>
              <option value="expert">Material Expert</option>
              <option value="reviewer">Reviewer</option>
              <option value="analyst">Procurement Analyst</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          {error && <div className={styles.error} style={{ color: 'red', marginBottom: '16px', fontSize: '14px' }}>{error}</div>}

          <button type="submit" className={styles.button} disabled={isLoading}>
            {isLoading ? 'Authenticating...' : 'Secure Login'}
          </button>
        </form>

        <div className={styles.rolesHint}>
          Authorized Personnel Only. Strictly monitored.
        </div>
      </div>
    </div>
  );
};

export default Login;
