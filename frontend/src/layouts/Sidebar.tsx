import { NavLink } from 'react-router-dom';
import clsx from 'clsx';
import {
  LayoutDashboard,
  UploadCloud,
  Dna,
  BrainCircuit,
  CheckSquare,
  Database,
  Network,
  Map as MapIcon,
  Briefcase,
  TrendingUp,
  FileCheck2,
  BarChart3,
  History,
  Link,
  Settings,
  Bot
} from 'lucide-react';
import styles from './Sidebar.module.css';

const navItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, path: '/overview' },
  { id: 'ingestion', label: 'Material Ingestion', icon: UploadCloud, path: '/ingestion' },
  { id: 'dna', label: 'Material DNA', icon: Dna, path: '/dna' },
  { id: 'matching', label: 'AI Matching', icon: BrainCircuit, path: '/matching' },
  { id: 'validation', label: 'Review & Validation', icon: CheckSquare, path: '/validation' },
  { id: 'master', label: 'National Material Master', icon: Database, path: '/master' },
  { id: 'graph', label: 'Material Knowledge Graph', icon: Network, path: '/graph' },
  { id: 'map', label: 'National Intelligence Map', icon: MapIcon, path: '/map' },
  { id: 'vendor', label: 'Vendor Intelligence', icon: Briefcase, path: '/vendor' },
  { id: 'procurement', label: 'Procurement Intelligence', icon: TrendingUp, path: '/procurement' },
  { id: 'passport', label: 'Material Passport', icon: FileCheck2, path: '/passport' },
  { id: 'copilot', label: 'AI Copilot', icon: Bot, path: '/copilot' },
  { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/analytics' },
  { id: 'audit', label: 'Audit Trail', icon: History, path: '/audit' },
  { id: 'integration', label: 'ERP / SAP Integration', icon: Link, path: '/integration' },
  { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
];

const Sidebar = () => {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logoContainer}>
        <div className={styles.logoTitle}>AI-POWERED</div>
        <div className={styles.logoSubtitle}>National Material Master</div>
      </div>
      <nav className={styles.nav}>
        <ul className={styles.navList}>
          {navItems.map((item) => (
            <li key={item.id}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  clsx(styles.navItem, isActive && styles.active)
                }
              >
                <item.icon className={styles.icon} />
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
