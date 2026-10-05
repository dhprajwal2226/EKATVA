import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

import styles from './Login.module.css';

const DEMO_EMAIL = 'reviewer@ekatva.demo';
const DEMO_PASSWORD = 'Demo@12345';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [cpse, setCpse] = useState('');
  const [role, setRole] = useState('admin');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const fillDemo = () => {
    setEmail(DEMO_EMAIL);
    setPassword(DEMO_PASSWORD);
    setCpse('ministry');
    setRole('reviewer');
    setError('');
  };

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

        <div
          style={{
            border: '1px dashed #3b82f6',
            background: 'rgba(59, 130, 246, 0.08)',
            borderRadius: '8px',
            padding: '12px 14px',
            marginBottom: '20px',
            fontSize: '13px',
            lineHeight: 1.5,
          }}
        >
          <div style={{ fontWeight: 600, marginBottom: '6px' }}>Demo access for evaluators</div>
          <div>Email: <code>{DEMO_EMAIL}</code></div>
          <div>Password: <code>{DEMO_PASSWORD}</code></div>
          <button
            type="button"
            onClick={fillDemo}
            style={{
              marginTop: '10px',
              padding: '6px 12px',
              fontSize: '13px',
              cursor: 'pointer',
              borderRadius: '6px',
              border: '1px solid #3b82f6',
              background: 'transparent',
              color: '#3b82f6',
              fontWeight: 600,
            }}
          >
            Fill demo credentials
          </button>
          <div style={{ marginTop: '8px', opacity: 0.75 }}>
            The first login may take up to a minute while the server wakes up.
          </div>
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
            <select
              className={styles.select}
              required
              value={cpse}
              onChange={(e) => setCpse(e.target.value)}
            >
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
            <select
              className={styles.select}
              required
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
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
