import { useState, useEffect } from 'react';
import { TrendingDown, TrendingUp, AlertTriangle, PackageSearch, Activity, AlertCircle } from 'lucide-react';
import { getProcurementIntelligence } from '../services/procurement';
import type { ExecutiveSummaryResponse } from '../types/api';
import styles from './Procurement.module.css';

const Procurement = () => {
  const [data, setData] = useState<ExecutiveSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProcurementData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await getProcurementIntelligence();
        setData(response);
      } catch (err: any) {
        console.error('Error fetching procurement intelligence:', err);
        setError(err.message || 'Failed to load procurement intelligence');
      } finally {
        setLoading(false);
      }
    };
    fetchProcurementData();
  }, []);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p>Loading procurement intelligence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <AlertCircle size={48} className={styles.errorIcon} />
          <h2>Error Loading Data</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>Procurement Intelligence</h1>
          <p className={styles.subtitle}>Analyze savings, vendor performance, and cross-CPSE procurement opportunities.</p>
        </div>
      </div>

      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Total Savings Identified</span>
            <TrendingDown size={20} className={styles.trendNegative} />
          </div>
          <div className={styles.kpiValue}>Unavailable</div>
          <div className={styles.trend + ' ' + styles.trendNegative}>
            <AlertCircle size={14} /> Data unavailable in system
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Joint Procurement Opps</span>
            <PackageSearch size={20} className={styles.trendPositive} />
          </div>
          <div className={styles.kpiValue}>{data?.multi_cpse_materials || 0} SKUs</div>
          <div className={styles.trend + ' ' + styles.trendPositive}>
            <TrendingUp size={14} /> High feasibility
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Vendor Risk Incidents</span>
            <AlertTriangle size={20} className={styles.trendNegative} />
          </div>
          <div className={styles.kpiValue}>Unavailable</div>
          <div className={styles.trend + ' ' + styles.trendNegative}>
            <AlertCircle size={14} /> Data unavailable in system
          </div>
        </div>
        
        <div className={styles.kpiCard}>
          <div className={styles.kpiHeader}>
            <span className={styles.kpiTitle}>Active Tenders Monitored</span>
            <Activity size={20} className={styles.trendPositive} />
          </div>
          <div className={styles.kpiValue}>Unavailable</div>
          <div className={styles.trend + ' ' + styles.trendPositive}>
            <AlertCircle size={14} /> Data unavailable in system
          </div>
        </div>
      </div>

      <div className={styles.chartsGrid}>
        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Cumulative Cost Savings (Through Standardization)</h3>
          <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
             <div style={{ textAlign: 'center', color: '#64748b' }}>
               <AlertCircle size={32} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.5 }} />
               <p>Chart data unavailable</p>
             </div>
          </div>
        </div>

        <div className={styles.chartCard}>
          <h3 className={styles.chartTitle}>Top Vendors by Volume</h3>
          <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
             <div style={{ textAlign: 'center', color: '#64748b' }}>
               <AlertCircle size={32} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.5 }} />
               <p>Chart data unavailable</p>
             </div>
          </div>
        </div>
      </div>

      <div className={styles.chartCard}>
        <h3 className={styles.chartTitle}>Joint Procurement Opportunities</h3>
        
        {data?.top_multi_cpse_materials && data.top_multi_cpse_materials.length > 0 ? (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>CNMC ID</th>
                <th>Material Description</th>
                <th>Interested CPSEs</th>
                <th>Est. Volume</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.top_multi_cpse_materials.map((opp, idx) => (
                <tr key={idx}>
                  <td><strong style={{ color: 'var(--color-primary)' }}>{opp.cnmc}</strong></td>
                  <td>-</td>
                  <td>{opp.count} CPSE(s)</td>
                  <td>-</td>
                  <td><span className={styles.badge + ' ' + styles.badgeOpt}>Potential</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: '#64748b', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
            <AlertCircle size={32} style={{ margin: '0 auto 16px', display: 'block', opacity: 0.5 }} />
            <p>No joint procurement opportunities identified yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Procurement;
