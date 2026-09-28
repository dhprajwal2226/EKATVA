import { Search, Bell, HelpCircle } from 'lucide-react';
import styles from './Topbar.module.css';

const Topbar = () => {
  return (
    <header className={styles.topbar}>
      <div className={styles.leftSection}>
        <div className={styles.searchContainer}>
          <Search className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search materials, CNMC, vendors..." 
            className={styles.searchInput}
          />
        </div>
        <div className={styles.statusIndicator}>
          <div className={styles.statusDot}></div>
          National Master: Operational
        </div>
      </div>
      
      <div className={styles.rightSection}>
        <HelpCircle className={styles.actionIcon} />
        <Bell className={styles.actionIcon} />
        
        <div className={styles.divider}></div>
        
        <div className={styles.profileSection}>
          <div className={styles.userInfo}>
            <span className={styles.userName}>Ministry of Steel</span>
            <span className={styles.userRole}>System Administrator</span>
          </div>
          <div className={styles.avatar}>MS</div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
