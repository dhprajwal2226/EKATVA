import { Fingerprint } from 'lucide-react';
import styles from './MaterialDNA.module.css';

const MaterialDNA = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Material DNA</h1>
        <p className={styles.subtitle}>Convert unstructured material descriptions into a technical material fingerprint.</p>
      </div>

      <div className={styles.mainCard}>
        <div className={styles.sourceSection}>
          <h2 className={styles.sectionTitle}>Source Descriptions</h2>
          <div className={styles.sourceDescriptions}>
            <div className={styles.sourceRow}>
              <span className={styles.cpseTag}>IOCL</span>
              <span className={styles.sourceText}>CS PIPE 10 INCH SCH40</span>
            </div>
            <div className={styles.sourceRow}>
              <span className={styles.cpseTag}>NTPC</span>
              <span className={styles.sourceText}>CARBON STEEL PIPE 10 IN SCHEDULE 40</span>
            </div>
            <div className={styles.sourceRow}>
              <span className={styles.cpseTag}>BHEL</span>
              <span className={styles.sourceText}>CS SEAMLESS PIPE 10 IN SCH 40</span>
            </div>
          </div>
        </div>

        <div className={styles.visualizationArea}>
          <div className={styles.fingerprintHeader}>
            <Fingerprint className={styles.fingerprintIcon} />
            <h2 className={styles.title} style={{ fontSize: '1.25rem' }}>Technical Fingerprint</h2>
          </div>
          
          <div className={styles.dnaGrid}>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Material Type</span>
              <span className={styles.nodeValue}>PIPE</span>
              <div className={styles.confidenceBadge}>100%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Material</span>
              <span className={styles.nodeValue}>CARBON STEEL</span>
              <div className={styles.confidenceBadge}>99%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Grade</span>
              <span className={styles.nodeValue}>ASTM A106</span>
              <div className={styles.confidenceBadge}>85%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Diameter</span>
              <span className={styles.nodeValue}>10 IN</span>
              <div className={styles.confidenceBadge}>100%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Schedule</span>
              <span className={styles.nodeValue}>40</span>
              <div className={styles.confidenceBadge}>100%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Form</span>
              <span className={styles.nodeValue}>SEAMLESS</span>
              <div className={styles.confidenceBadge}>92%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Standard</span>
              <span className={styles.nodeValue}>ASME B36.10</span>
              <div className={styles.confidenceBadge}>95%</div>
            </div>
            <div className={styles.dnaNode}>
              <span className={styles.nodeLabel}>Application</span>
              <span className={styles.nodeValue}>PROCESS PIPING</span>
              <div className={styles.confidenceBadge}>88%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaterialDNA;
