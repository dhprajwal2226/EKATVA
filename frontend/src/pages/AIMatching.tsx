import { BrainCircuit, Check, CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';
import styles from './AIMatching.module.css';

const AIMatching = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>AI Material Matching</h1>
          <p className={styles.subtitle}>Comparing CPSE records using Fuzzy Similarity, Semantic Embeddings, and Technical Rules.</p>
        </div>
        <div className={styles.badge + ' ' + styles.badgeMatch}>
          <CheckCircle2 size={16} /> Potential Same Material
        </div>
      </div>

      <div className={styles.matchContainer}>
        {/* Left Record */}
        <div className={styles.recordCard}>
          <div className={styles.recordHeader}>
            <span className={styles.cpseName}>IOCL</span>
            <span className={styles.materialCode}>101</span>
          </div>
          <div className={styles.recordDesc}>
            CS PIPE 10 INCH SCH40
          </div>
          <div className={styles.pipelineFlow}>
            Extracted DNA: PIPE, CARBON STEEL, 10 INCH, SCH40
          </div>
        </div>

        {/* AI Analysis Center */}
        <div className={styles.analysisCard}>
          <div className={styles.analysisTitle}>AI Confidence</div>
          <div className={styles.scoreCircle}>
            <span className={styles.scoreValue}>98%</span>
            <span className={styles.scoreLabel}>MATCH</span>
          </div>
          
          <div className={styles.scoreMetrics}>
            <div className={styles.metricRow}>
              <span>Semantic Similarity</span>
              <span className={styles.metricValue}>97%</span>
            </div>
            <div className={styles.metricRow}>
              <span>Attribute Match</span>
              <span className={styles.metricValue}>100%</span>
            </div>
            <div className={styles.metricRow}>
              <span>Tech Compatibility</span>
              <span className={styles.metricValue}>98%</span>
            </div>
          </div>
        </div>

        {/* Right Record */}
        <div className={styles.recordCard}>
          <div className={styles.recordHeader}>
            <span className={styles.cpseName}>NTPC</span>
            <span className={styles.materialCode}>P-782</span>
          </div>
          <div className={styles.recordDesc}>
            CARBON STEEL PIPE 10 IN SCHEDULE 40
          </div>
          <div className={styles.pipelineFlow}>
            Extracted DNA: PIPE, CARBON STEEL, 10 IN, SCHEDULE 40
          </div>
        </div>
      </div>

      {/* Explainable AI Section */}
      <div className={styles.explainableSection}>
        <div className={styles.explainCard}>
          <h3 className={styles.explainTitle}>
            <CheckCircle2 size={20} className={styles.reasonIcon + ' ' + styles.success} /> 
            Why This Match?
          </h3>
          <div className={styles.reasonList}>
            <div className={styles.reasonItem}>
              <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
              <span>Same material type (PIPE)</span>
            </div>
            <div className={styles.reasonItem}>
              <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
              <span>Same material grade (CARBON STEEL)</span>
            </div>
            <div className={styles.reasonItem}>
              <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
              <span>Same diameter (10 INCH)</span>
            </div>
            <div className={styles.reasonItem}>
              <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
              <span>Same schedule (40)</span>
            </div>
            <div className={styles.reasonItem}>
              <Check size={16} className={styles.reasonIcon + ' ' + styles.success} />
              <span>Different wording normalized (CS → CARBON STEEL)</span>
            </div>
          </div>
        </div>

        <div className={styles.explainCard}>
          <h3 className={styles.explainTitle}>
            <AlertTriangle size={20} className={styles.reasonIcon + ' ' + styles.warning} /> 
            Technical Differences
          </h3>
          <div className={styles.reasonList}>
            <div className={styles.reasonItem}>
              <AlertTriangle size={16} className={styles.reasonIcon + ' ' + styles.warning} />
              <span>Vendor differs between IOCL and NTPC records.</span>
            </div>
            <div className={styles.reasonItem}>
              <AlertTriangle size={16} className={styles.reasonIcon + ' ' + styles.warning} />
              <span>CPSE-specific naming conventions applied.</span>
            </div>
          </div>
        </div>

        {/* Explainable Reasoning Summary */}
        <div className={styles.summaryBox}>
          <BrainCircuit size={24} className={styles.summaryIcon} />
          <div className={styles.summaryContent}>
            <h3>AI Reasoning Summary</h3>
            <p>
              Both records describe a carbon steel seamless pipe with the same diameter, schedule and technical standard. Differences are limited to naming conventions and source-specific metadata.
            </p>
          </div>
        </div>
      </div>

      {/* Example of Critical Difference Warning (Mocked below) */}
      <div className={styles.header} style={{ marginTop: '40px' }}>
        <div className={styles.titleGroup}>
          <h2 className={styles.title} style={{ fontSize: '1.25rem' }}>Conflict Detection Example</h2>
          <p className={styles.subtitle}>Demonstrating semantic similarities that hide critical technical conflicts.</p>
        </div>
        <div className={styles.badge + ' ' + styles.badgeConflict}>
          <ShieldAlert size={16} /> DO NOT AUTO-MERGE
        </div>
      </div>

      <div className={styles.summaryBox} style={{ backgroundColor: 'var(--color-danger-bg)', borderColor: 'rgba(225, 29, 72, 0.2)' }}>
        <AlertTriangle size={24} style={{ color: 'var(--color-danger)' }} />
        <div className={styles.summaryContent}>
          <h3 style={{ color: 'var(--color-danger)' }}>CRITICAL TECHNICAL DIFFERENCE</h3>
          <p>
            <strong>IOCL (SS304 VALVE 4 INCH 150#)</strong> vs <strong>NTPC (SS316 VALVE 4 INCH 150#)</strong><br />
            Material grade affects technical equivalence (SS304 vs SS316). AI has blocked automatic merge. Requires Technical Expert Review.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIMatching;
