import { useState } from 'react';
import { Check, X, Edit3, ShieldCheck, AlertCircle } from 'lucide-react';
import styles from './Validation.module.css';

const Validation = () => {
  const [status, setStatus] = useState<'pending' | 'approved'>('pending');

  const handleApprove = () => {
    setStatus('approved');
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>AI Review Queue</h1>
          <p className={styles.subtitle}>Human expert validation for AI-generated material clusters.</p>
        </div>
      </div>

      {status === 'pending' ? (
        <div className={styles.clusterCard}>
          <div className={styles.clusterHeader}>
            <div className={styles.clusterInfo}>
              <span className={styles.clusterId}>Cluster: CL-8429</span>
              <span className={styles.badge + ' ' + styles.badgeSuccess}>High Confidence Match (98%)</span>
              <span className={styles.badge + ' ' + styles.badgeWarning}>UNSPSC: 23141601</span>
            </div>
            <div className={styles.actionButtons}>
              <button className={styles.btn + ' ' + styles.btnReject}><X size={16} /> Reject</button>
              <button className={styles.btn + ' ' + styles.btnEdit}><Edit3 size={16} /> Edit</button>
              <button className={styles.btn + ' ' + styles.btnApprove} onClick={handleApprove}><Check size={16} /> Approve</button>
            </div>
          </div>

          <div className={styles.candidatesGrid}>
            <div className={styles.candidateCard}>
              <div className={styles.candidateHeader}>
                <span className={styles.cpseTag}>IOCL</span>
                <span className={styles.materialCode}>101</span>
              </div>
              <div className={styles.candidateDesc}>CS PIPE 10 INCH SCH40</div>
              <div className={styles.attributesList}>
                <div className={styles.attribute}><span className={styles.attrLabel}>Type</span><span className={styles.attrValue}>PIPE</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Material</span><span className={styles.attrValue}>CARBON STEEL</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Size</span><span className={styles.attrValue}>10 INCH</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Schedule</span><span className={styles.attrValue}>SCH40</span></div>
              </div>
            </div>

            <div className={styles.candidateCard}>
              <div className={styles.candidateHeader}>
                <span className={styles.cpseTag}>NTPC</span>
                <span className={styles.materialCode}>P-782</span>
              </div>
              <div className={styles.candidateDesc}>CARBON STEEL PIPE 10 IN SCHEDULE 40</div>
              <div className={styles.attributesList}>
                <div className={styles.attribute}><span className={styles.attrLabel}>Type</span><span className={styles.attrValue}>PIPE</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Material</span><span className={styles.attrValue}>CARBON STEEL</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Size</span><span className={styles.attrValue}>10 IN</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Schedule</span><span className={styles.attrValue}>SCHEDULE 40</span></div>
              </div>
            </div>

            <div className={styles.candidateCard}>
              <div className={styles.candidateHeader}>
                <span className={styles.cpseTag}>BHEL</span>
                <span className={styles.materialCode}>PIPE-55</span>
              </div>
              <div className={styles.candidateDesc}>CS SEAMLESS PIPE 10 IN SCH 40</div>
              <div className={styles.attributesList}>
                <div className={styles.attribute}><span className={styles.attrLabel}>Type</span><span className={styles.attrValue}>PIPE</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Material</span><span className={styles.attrValue}>CS</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Size</span><span className={styles.attrValue}>10 IN</span></div>
                <div className={styles.attribute}><span className={styles.attrLabel}>Schedule</span><span className={styles.attrValue}>SCH 40</span></div>
              </div>
            </div>
          </div>

          <div className={styles.commentSection}>
            <div className={styles.commentHeader}>Reviewer Comment (Optional)</div>
            <textarea 
              className={styles.commentInput} 
              placeholder="e.g., Verified against technical specification."
            ></textarea>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-primary)', fontWeight: 500, fontSize: '0.875rem' }}>
              <AlertCircle size={16} /> AI recommends → Human decides
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.messageBox}>
          <ShieldCheck size={20} />
          Cluster Approved. CNMC generated successfully and moved to National Master.
        </div>
      )}
    </div>
  );
};

export default Validation;
