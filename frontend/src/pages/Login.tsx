import { useNavigate } from 'react-router-dom';
import styles from './Login.module.css';

const Login = () => {
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/overview');
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
              required 
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Password</label>
            <input 
              type="password" 
              className={styles.input} 
              placeholder="Enter your password" 
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

          <button type="submit" className={styles.button}>
            Secure Login
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
