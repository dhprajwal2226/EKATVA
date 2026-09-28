import { Database, Copy, CheckCircle, Network, TrendingUp } from 'lucide-react';
import clsx from 'clsx';
import styles from './Overview.module.css';

const Overview = () => {
  return (
    <div className={styles.overviewContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>National Material Intelligence</h1>
        <p className={styles.subtitle}>Unified visibility across participating CPSE material masters.</p>
      </div>

      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>Total Material Records</span>
            <Database className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>24,860</div>
          <div className={styles.kpiFooter}>
            <span className={styles.trendUp}><TrendingUp className={styles.trendIcon} /> 2.4%</span>
            from last month
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>Potential Duplicates</span>
            <Copy className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>3,842</div>
          <div className={styles.kpiFooter}>
            <span className={styles.trendUp}><TrendingUp className={styles.trendIcon} /> 1.2%</span>
            detected recently
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>CNMCs Generated</span>
            <CheckCircle className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>1,126</div>
          <div className={styles.kpiFooter}>
            <span className={styles.trendUp}><TrendingUp className={styles.trendIcon} /> 5.8%</span>
            approved
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>CPSEs Connected</span>
            <Network className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>8</div>
          <div className={styles.kpiFooter}>
            <span>Active integrations</span>
          </div>
        </div>
      </div>

      <div className={styles.mainGrid}>
        <div className={styles.sectionCard}>
          <h2 className={styles.sectionTitle}>AI Matching Activity</h2>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Identical Matches Detected</span>
              <span className={styles.activityValue}>1,245</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Near-Duplicates</span>
              <span className={styles.activityValue}>843</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Technical Conflicts Found</span>
              <span className={styles.activityValue} style={{ color: 'var(--color-danger)' }}>112</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Functionally Equivalent</span>
              <span className={styles.activityValue}>450</span>
            </div>
          </div>
        </div>

        <div className={styles.sectionCard}>
          <h2 className={styles.sectionTitle}>Validation Queue</h2>
          <div className={styles.queueList}>
            <div className={clsx(styles.queueItem, styles.success)}>
              <div className={styles.queueInfo}>
                <span className={styles.queueTitle}>High Confidence Match (98%)</span>
                <span className={styles.queueDesc}>IOCL-101 ↔ NTPC-P-782 (CS PIPE 10")</span>
              </div>
              <button className={styles.queueAction}>Review</button>
            </div>
            <div className={clsx(styles.queueItem, styles.critical)}>
              <div className={styles.queueInfo}>
                <span className={styles.queueTitle}>Critical Technical Conflict</span>
                <span className={styles.queueDesc}>Grade Mismatch: SS304 vs SS316</span>
              </div>
              <button className={styles.queueAction}>Resolve</button>
            </div>
            <div className={styles.queueItem}>
              <div className={styles.queueInfo}>
                <span className={styles.queueTitle}>Pending Expert Decision</span>
                <span className={styles.queueDesc}>BHEL-PIPE-55 Manufacturer Review</span>
              </div>
              <button className={styles.queueAction}>Review</button>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.sectionCard}>
        <h2 className={styles.sectionTitle}>National Material Distribution</h2>
        <div className={styles.mapPlaceholder}>
          Interactive India Map Preview (Loading Leaflet...)
        </div>
      </div>

      <div className={styles.sectionCard}>
        <h2 className={styles.sectionTitle}>Recent Material Decisions</h2>
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Material Description</th>
                <th>CPSEs</th>
                <th>Match Type</th>
                <th>Status</th>
                <th>Reviewer</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>CS SEAMLESS PIPE 10 IN SCH 40</td>
                <td>IOCL, NTPC, BHEL</td>
                <td>Identical</td>
                <td><span className={clsx(styles.badge, styles.success)}>Approved</span></td>
                <td>Reviewer A</td>
                <td>Oct 12, 2026</td>
              </tr>
              <tr>
                <td>SS VALVE 4 INCH 150#</td>
                <td>IOCL, GAIL</td>
                <td>Conflict</td>
                <td><span className={clsx(styles.badge, styles.warning)}>Pending</span></td>
                <td>Expert B</td>
                <td>Oct 12, 2026</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Overview;
