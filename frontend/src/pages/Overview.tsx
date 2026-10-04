import { useEffect, useState } from 'react';
import { Database, Copy, CheckCircle, Network, TrendingUp } from 'lucide-react';
import styles from './Overview.module.css';
import { getOverview } from '../services/analytics';
import type { OverviewAnalyticsResponse } from '../types/api';

const Overview = () => {
  const [data, setData] = useState<OverviewAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getOverview()
      .then(res => {
        setData(res);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message || 'Failed to load analytics data.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className={styles.overviewContainer} style={{ padding: '2rem' }}>Loading dashboard data...</div>;
  }

  if (error) {
    return <div className={styles.overviewContainer} style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  }

  const hasData = data && data.national_materials > 0;

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
          <div className={styles.kpiValue}>{data?.national_materials.toLocaleString() ?? 0}</div>
          <div className={styles.kpiFooter}>
            {hasData ? (
              <>
                <span className={styles.trendUp}><TrendingUp className={styles.trendIcon} /> 2.4%</span>
                from last month
              </>
            ) : (
              <span>No historical data available</span>
            )}
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>Potential Duplicates</span>
            <Copy className={styles.kpiIcon} />
          </div>
          {/* No direct backend equivalent for "Potential Duplicates" available, using empty state */}
          <div className={styles.kpiValue}>-</div>
          <div className={styles.kpiFooter}>
            <span>Data unavailable</span>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>CNMCs Generated</span>
            <CheckCircle className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>{data?.active_materials.toLocaleString() ?? 0}</div>
          <div className={styles.kpiFooter}>
            {hasData ? (
              <>
                <span className={styles.trendUp}><TrendingUp className={styles.trendIcon} /> 5.8%</span>
                approved
              </>
            ) : (
              <span>No historical data available</span>
            )}
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>CPSEs Connected</span>
            <Network className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>{data?.cpse_count.toLocaleString() ?? 0}</div>
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
              <span className={styles.activityValue}>-</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Near-Duplicates</span>
              <span className={styles.activityValue}>-</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Technical Conflicts Found</span>
              <span className={styles.activityValue}>-</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Functionally Equivalent</span>
              <span className={styles.activityValue}>-</span>
            </div>
          </div>
        </div>

        <div className={styles.sectionCard}>
          <h2 className={styles.sectionTitle}>Validation Queue</h2>
          {data?.pending_reviews ? (
            <div className={styles.queueList}>
              <div className={styles.queueItem}>
                <div className={styles.queueInfo}>
                  <span className={styles.queueTitle}>Pending Reviews</span>
                  <span className={styles.queueDesc}>{data.pending_reviews} matches require expert validation.</span>
                </div>
                <button className={styles.queueAction}>Review</button>
              </div>
            </div>
          ) : (
            <div style={{ padding: '1rem', color: '#666', fontStyle: 'italic' }}>
              Validation queue is empty.
            </div>
          )}
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
                <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                  No recent decisions available.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Overview;
