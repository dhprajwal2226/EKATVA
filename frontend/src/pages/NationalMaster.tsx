import { Database, Link2, ShieldCheck, CheckCircle2, AlertTriangle, Fingerprint } from 'lucide-react';
import styles from './NationalMaster.module.css';

const NationalMaster = () => {
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
            <div className={styles.cnmcId}>CNMC-000001</div>
            <div className={styles.cnmcDesc}>Carbon Steel Seamless Pipe 10 Inch Schedule 40</div>
          </div>
          <div>
            <span style={{ backgroundColor: 'var(--color-primary-light)', color: 'white', padding: '6px 16px', borderRadius: '20px', fontSize: '0.875rem', fontWeight: 600 }}>
              UNSPSC: 23141601
            </span>
          </div>
        </div>

        <div className={styles.metaInfo} style={{ marginBottom: '24px' }}>
          <div className={styles.metaItem}>
            <Database size={16} /> 3 CPSEs
          </div>
          <div className={styles.metaItem}>
            <ShieldCheck size={16} /> Approved Oct 12, 2026
          </div>
        </div>

        <div className={styles.sectionGrid}>
          <div className={styles.sectionBox}>
            <h3 className={styles.sectionTitle}><Link2 size={18} /> Mapped CPSE Codes</h3>
            <div className={styles.mappingList}>
              <div className={styles.mappingRow}>
                <div className={styles.mappingLeft}>
                  <span className={styles.cpseTag}>IOCL</span>
                  <span className={styles.mappingCode}>101</span>
                </div>
                <div className={styles.mappingStatus}><CheckCircle2 size={14} /> Mapped</div>
              </div>
              <div className={styles.mappingRow}>
                <div className={styles.mappingLeft}>
                  <span className={styles.cpseTag}>NTPC</span>
                  <span className={styles.mappingCode}>P-782</span>
                </div>
                <div className={styles.mappingStatus}><CheckCircle2 size={14} /> Mapped</div>
              </div>
              <div className={styles.mappingRow}>
                <div className={styles.mappingLeft}>
                  <span className={styles.cpseTag}>BHEL</span>
                  <span className={styles.mappingCode}>PIPE-55</span>
                </div>
                <div className={styles.mappingStatus}><CheckCircle2 size={14} /> Mapped</div>
              </div>
            </div>
            
            <div className={styles.traceabilityNote}>
              <AlertTriangle size={18} />
              Existing CPSE codes remain unchanged and traceable.
            </div>
          </div>

          <div className={styles.sectionBox}>
            <h3 className={styles.sectionTitle}><Fingerprint size={18} /> Technical Attributes</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.875rem' }}>
              <div><strong style={{ color: 'var(--color-text-secondary)' }}>Material:</strong> Carbon Steel</div>
              <div><strong style={{ color: 'var(--color-text-secondary)' }}>Form:</strong> Seamless</div>
              <div><strong style={{ color: 'var(--color-text-secondary)' }}>Size:</strong> 10 Inch</div>
              <div><strong style={{ color: 'var(--color-text-secondary)' }}>Schedule:</strong> 40</div>
              <div><strong style={{ color: 'var(--color-text-secondary)' }}>Standard:</strong> ASME B36.10</div>
            </div>

            <div className={styles.leadingReason}>
              <ShieldCheck className={styles.leadingIcon} size={24} />
              <div className={styles.leadingContent}>
                <h4>Leading Material Selection</h4>
                <p>NTPC record selected as the leading description due to highest attribute completeness and strict adherence to standard naming conventions.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NationalMaster;
