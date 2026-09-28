import { ArrowRight } from 'lucide-react';
import styles from './Normalization.module.css';

const Normalization = () => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Data Normalization</h1>
        <p className={styles.subtitle}>Standardize terminology, handle unit conversions, and correct formatting before AI matching.</p>
      </div>

      <div className={styles.card}>
        <div className={styles.comparisonSection}>
          <div className={styles.valueBox}>
            <div className={styles.valueLabel}>Original Input</div>
            <div className={styles.valueText}>SS BOLT M16 X 50MM</div>
          </div>
          
          <div className={styles.arrow}>
            <ArrowRight />
          </div>
          
          <div className={styles.valueBox + ' ' + styles.normalized}>
            <div className={styles.valueLabel}>Normalized Output</div>
            <div className={styles.valueText}>STAINLESS STEEL HEX BOLT M16 X 50 MM</div>
          </div>
        </div>

        <h2 className={styles.sectionTitle}>Applied Transformations</h2>
        <table className={styles.transformTable}>
          <thead>
            <tr>
              <th>Transformation Type</th>
              <th>Original Value</th>
              <th>Normalized Value</th>
              <th>AI Confidence</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Abbreviation Expansion</td>
              <td><span className={styles.originalText}>SS</span></td>
              <td><span className={styles.newText}>STAINLESS STEEL</span></td>
              <td className={styles.confidenceHigh}>99%</td>
            </tr>
            <tr>
              <td>Implicit Context Addition</td>
              <td><span className={styles.originalText}>BOLT M16</span></td>
              <td><span className={styles.newText}>HEX BOLT M16</span></td>
              <td className={styles.confidenceMed}>92%</td>
            </tr>
            <tr>
              <td>Spacing Standardization</td>
              <td><span className={styles.originalText}>50MM</span></td>
              <td><span className={styles.newText}>50 MM</span></td>
              <td className={styles.confidenceHigh}>100%</td>
            </tr>
          </tbody>
        </table>

        <div style={{ marginTop: '40px' }}>
          <h2 className={styles.sectionTitle}>Unit Conversion Examples</h2>
          <table className={styles.transformTable}>
            <thead>
              <tr>
                <th>Original System</th>
                <th>Target Metric</th>
                <th>Conversion Rule</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1 INCH</td>
                <td>25.4 MM</td>
                <td>Imperial to Metric (Length)</td>
              </tr>
              <tr>
                <td>150 PSI</td>
                <td>10.34 BAR</td>
                <td>Imperial to Metric (Pressure)</td>
              </tr>
              <tr>
                <td>2 LBS</td>
                <td>0.907 KG</td>
                <td>Imperial to Metric (Weight)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Normalization;
