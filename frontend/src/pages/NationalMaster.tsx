import { useState, useEffect } from 'react';
import { Database, Link2, ShieldCheck, CheckCircle2, AlertTriangle, Fingerprint } from 'lucide-react';
import styles from './NationalMaster.module.css';
import { cnmcService } from '../services/cnmc';
import type { CNMCDetailResponse } from '../types/api';

const NationalMaster = () => {
  const [data, setData] = useState<CNMCDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFirstCnmc = async () => {
      try {
        setLoading(true);
        const res = await cnmcService.getCNMCs({ page: 1, page_size: 1 });
        if (res.items && res.items.length > 0) {
          setData(res.items[0]);
        } else {
          setData(null);
        }
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch national master material');
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchFirstCnmc();
  }, []);

  if (loading) {
    return <div className={styles.container}><div style={{ padding: '24px' }}>Loading national material...</div></div>;
  }

  if (error) {
    return <div className={styles.container}><div style={{ padding: '24px', color: 'red' }}>Error: {error}</div></div>;
  }

  if (!data) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.titleGroup}>
            <h1 className={styles.title}>National Material Master</h1>
            <p className={styles.subtitle}>The unified, standardized catalog of materials across all participating CPSEs.</p>
          </div>
        </div>
        <div style={{ padding: '24px', backgroundColor: 'white', borderRadius: '8px', border: '1px solid var(--color-border)', marginTop: '24px' }}>
          No national materials available in the database.
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>National Material Master</h1>
          <p className={styles.subtitle}>The unified, standardized catalog of materials across all participating CPSEs.</p>
        </div>
      </div>

      <div className={styles.cnmcCard}>
        <div className={styles.cnmcHeader}>
          <div>
            <div className={styles.cnmcId}>{data.cnmc}</div>
            <div className={styles.cnmcDesc}>{data.standard_description}</div>
          </div>
          <div>
            {data.category && (
              <span style={{ backgroundColor: 'var(--color-primary-light)', color: 'white', padding: '6px 16px', borderRadius: '20px', fontSize: '0.875rem', fontWeight: 600 }}>
                {data.category}
              </span>
            )}
          </div>
        </div>

        <div className={styles.metaInfo} style={{ marginBottom: '24px' }}>
          <div className={styles.metaItem}>
            <Database size={16} /> {data.mappings.length} CPSE{data.mappings.length !== 1 ? 's' : ''}
          </div>
          <div className={styles.metaItem}>
            <ShieldCheck size={16} /> Status: {data.status}
          </div>
        </div>

        <div className={styles.sectionGrid}>
          <div className={styles.sectionBox}>
            <h3 className={styles.sectionTitle}><Link2 size={18} /> Mapped CPSE Codes</h3>
            {data.mappings.length > 0 ? (
              <div className={styles.mappingList}>
                {data.mappings.map((mapping) => (
                  <div key={mapping.id} className={styles.mappingRow}>
                    <div className={styles.mappingLeft}>
                      <span className={styles.cpseTag}>{mapping.cpse_code}</span>
                      <span className={styles.mappingCode}>{mapping.material_code}</span>
                    </div>
                    <div className={styles.mappingStatus}><CheckCircle2 size={14} /> {mapping.mapping_type}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '16px', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>No CPSE mappings found.</div>
            )}
            
            <div className={styles.traceabilityNote}>
              <AlertTriangle size={18} />
              Existing CPSE codes remain unchanged and traceable.
            </div>
          </div>

          <div className={styles.sectionBox}>
            <h3 className={styles.sectionTitle}><Fingerprint size={18} /> Technical Attributes</h3>
            {Object.keys(data.canonical_attributes || {}).length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.875rem' }}>
                {Object.entries(data.canonical_attributes).map(([key, value]) => (
                  value ? (
                    <div key={key}>
                      <strong style={{ color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>
                        {key.replace(/_/g, ' ')}:
                      </strong>{' '}
                      {value}
                    </div>
                  ) : null
                ))}
              </div>
            ) : (
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>No technical attributes available.</div>
            )}

            <div className={styles.leadingReason} style={{ marginTop: '24px' }}>
              <ShieldCheck className={styles.leadingIcon} size={24} />
              <div className={styles.leadingContent}>
                <h4>Identity Hash</h4>
                <p style={{ wordBreak: 'break-all', fontSize: '0.75rem', fontFamily: 'monospace' }}>{data.identity_hash}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NationalMaster;
