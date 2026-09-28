import { useState } from 'react';
import { UploadCloud, CheckCircle2, CircleDashed, FileSpreadsheet, Loader2 } from 'lucide-react';
import clsx from 'clsx';
import styles from './Ingestion.module.css';

const Ingestion = () => {
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'validating' | 'done'>('idle');

  const handleUpload = () => {
    setUploadState('uploading');
    setTimeout(() => setUploadState('validating'), 1500);
    setTimeout(() => setUploadState('done'), 3500);
  };

  return (
    <div className={styles.ingestionContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>Multi-CPSE Material Ingestion</h1>
        <p className={styles.subtitle}>Securely upload and validate material master data from participating CPSEs.</p>
      </div>

      <div className={styles.card}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Select Originating CPSE</label>
          <select className={styles.select} defaultValue="">
            <option value="" disabled>Select CPSE</option>
            <option value="iocl">IOCL</option>
            <option value="ntpc">NTPC</option>
            <option value="bhel">BHEL</option>
            <option value="gail">GAIL</option>
            <option value="other">Other CPSE</option>
          </select>
        </div>

        {uploadState === 'idle' && (
          <div className={styles.uploadZone} onClick={handleUpload}>
            <UploadCloud className={styles.uploadIcon} />
            <div className={styles.uploadTitle}>Drop material master file here</div>
            <div className={styles.uploadSubtitle}>or click to browse. Supports CSV, Excel, and JSON.</div>
            
            <div className={styles.supportedFields}>
              <span className={styles.fieldChip}>Material Code</span>
              <span className={styles.fieldChip}>Description</span>
              <span className={styles.fieldChip}>Category</span>
              <span className={styles.fieldChip}>Unit</span>
              <span className={styles.fieldChip}>Grade</span>
              <span className={styles.fieldChip}>Size</span>
              <span className={styles.fieldChip}>Standard</span>
              <span className={styles.fieldChip}>Manufacturer</span>
            </div>
          </div>
        )}

        {uploadState !== 'idle' && (
          <div className={styles.stepsContainer}>
            <div className={clsx(styles.step, styles.completed)}>
              <FileSpreadsheet className={styles.stepIcon} />
              <div className={styles.stepContent}>
                <div className={styles.stepTitle}>File Upload</div>
                <div className={styles.stepDesc}>ntpc_material_master_2026.csv (14.2 MB)</div>
              </div>
              <div className={styles.stepStatus}>Complete</div>
            </div>

            <div className={clsx(styles.step, uploadState === 'validating' ? styles.active : (uploadState === 'done' ? styles.completed : ''))}>
              {uploadState === 'validating' ? <Loader2 className={clsx(styles.stepIcon, 'animate-spin')} /> : (uploadState === 'done' ? <CheckCircle2 className={styles.stepIcon} /> : <CircleDashed className={styles.stepIcon} />)}
              <div className={styles.stepContent}>
                <div className={styles.stepTitle}>Step 1 → File Validation & Schema Detection</div>
                <div className={styles.stepDesc}>Checking for missing columns and malformed rows.</div>
              </div>
              <div className={styles.stepStatus}>{uploadState === 'validating' ? 'Processing...' : (uploadState === 'done' ? 'Complete' : 'Pending')}</div>
            </div>

            <div className={clsx(styles.step, uploadState === 'done' ? styles.active : '')}>
              {uploadState === 'done' ? <Loader2 className={clsx(styles.stepIcon, 'animate-spin')} /> : <CircleDashed className={styles.stepIcon} />}
              <div className={styles.stepContent}>
                <div className={styles.stepTitle}>Step 2 → Data Cleaning & Attribute Extraction</div>
                <div className={styles.stepDesc}>Normalizing text and extracting Material DNA.</div>
              </div>
              <div className={styles.stepStatus}>{uploadState === 'done' ? 'Processing...' : 'Pending'}</div>
            </div>
            
            {uploadState === 'done' && (
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ fontSize: '0.875rem', marginBottom: '8px' }}>Data Preview (First 3 rows)</h4>
                <table className={styles.previewTable}>
                  <thead>
                    <tr>
                      <th>Original Code</th>
                      <th>Original Description</th>
                      <th>Extracted Type</th>
                      <th>Extracted Grade</th>
                      <th>Extracted Size</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>P-782</td>
                      <td>CARBON STEEL PIPE 10 IN SCHEDULE 40</td>
                      <td>PIPE</td>
                      <td>CARBON STEEL</td>
                      <td>10 IN</td>
                    </tr>
                    <tr>
                      <td>V-220</td>
                      <td>SS316 VALVE 4 INCH 150#</td>
                      <td>VALVE</td>
                      <td>SS316</td>
                      <td>4 INCH</td>
                    </tr>
                    <tr>
                      <td>F-105</td>
                      <td>FLANGE WELD NECK 6" 300# RF CS</td>
                      <td>FLANGE</td>
                      <td>CS</td>
                      <td>6 INCH</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Ingestion;
