import { useEffect, useState } from 'react';
import { Database, Copy, CheckCircle, Network } from 'lucide-react';
import styles from './Overview.module.css';
import { getOverview } from '../services/analytics';
import type { OverviewAnalyticsResponse } from '../types/api';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) || 'http://localhost:8000';

async function matchTotal(classification: string): Promise<number | null> {
  try {
    const res = await fetch(`${API_BASE}/api/matching?classification=${classification}&page=1&page_size=1`);
    if (!res.ok) return null;
    const body = await res.json();
    return typeof body.total === 'number' ? body.total : null;
  } catch {
    return null;
  }
}

const fmt = (n: number | null | undefined) => (n === null || n === undefined ? '-' : n.toLocaleString());

const Overview = () => {
  const [data, setData] = useState<OverviewAnalyticsResponse | null>(null);
  const [matches, setMatches] = useState<Record<string, number | null>>({});
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

    const classes = ['IDENTICAL', 'NEAR_DUPLICATE', 'FUNCTIONALLY_EQUIVALENT', 'REVIEW_REQUIRED'];
    Promise.all(classes.map(c => matchTotal(c))).then(totals => {
      const out: Record<string, number | null> = {};
      classes.forEach((c, i) => (out[c] = totals[i]));
      setMatches(out);
    });
  }, []);

  if (loading) {
    return <div className={styles.overviewContainer} style={{ padding: '2rem' }}>Loading dashboard data...</div>;
  }

  if (error) {
    return <div className={styles.overviewContainer} style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
  }

  const potentialDuplicates =
    matches.IDENTICAL === undefined || matches.NEAR_DUPLICATE === undefined
      ? null
      : (matches.IDENTICAL ?? 0) + (matches.NEAR_DUPLICATE ?? 0);

  return (
    <div className={styles.overviewContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>National Material Intelligence</h1>
        <p className={styles.subtitle}>Unified visibility across participating CPSE material masters.</p>
      </div>

      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>National Materials (CNMCs)</span>
            <Database className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>{fmt(data?.national_materials ?? 0)}</div>
          <div className={styles.kpiFooter}><span>Common national codes issued</span></div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>Potential Duplicates</span>
            <Copy className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>{fmt(potentialDuplicates)}</div>
          <div className={styles.kpiFooter}><span>Identical + near-duplicate pairs</span></div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>Approved CNMCs</span>
            <CheckCircle className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>{fmt(data?.active_materials ?? 0)}</div>
          <div className={styles.kpiFooter}><span>Active after human approval</span></div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span>CPSEs Linked</span>
            <Network className={styles.kpiIcon} />
          </div>
          <div className={styles.kpiValue}>{fmt(data?.cpse_count ?? 0)}</div>
          <div className={styles.kpiFooter}><span>CPSEs with mapped materials</span></div>
        </div>
      </div>

      <div className={styles.mainGrid}>
        <div className={styles.sectionCard}>
          <h2 className={styles.sectionTitle}>AI Matching Activity</h2>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Identical Matches Detected</span>
              <span className={styles.activityValue}>{fmt(matches.IDENTICAL)}</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Near-Duplicates</span>
              <span className={styles.activityValue}>{fmt(matches.NEAR_DUPLICATE)}</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Functionally Equivalent</span>
              <span className={styles.activityValue}>{fmt(matches.FUNCTIONALLY_EQUIVALENT)}</span>
            </div>
            <div className={styles.activityItem}>
              <span className={styles.activityLabel}>Review Required (conflicts / missing specs)</span>
              <span className={styles.activityValue}>{fmt(matches.REVIEW_REQUIRED)}</span>
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
    </div>
  );
};

export default Overview;