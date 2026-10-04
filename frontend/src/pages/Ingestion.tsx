import { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, CircleDashed, FileSpreadsheet, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import clsx from 'clsx';
import styles from './Ingestion.module.css';
import { ingestionService } from '../services/ingestion';
import type { IngestionJobResponse } from '../types/api';

const Ingestion = () => {
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'validating' | 'done' | 'error'>('idle');
  const [selectedCpse, setSelectedCpse] = useState<string>('');
  const [jobResponse, setJobResponse] = useState<IngestionJobResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [selectedFileSize, setSelectedFileSize] = useState<number | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleZoneClick = () => {
    if (uploadState === 'idle') {
      fileInputRef.current?.click();
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFileName(file.name);
    setSelectedFileSize(file.size);
    setUploadState('uploading');
    setErrorMsg(null);
    setJobResponse(null);

    try {
      setUploadState('validating');
      const res = await ingestionService.uploadFile(file, selectedCpse || undefined);
      
      const jobDetails = await ingestionService.getJob(res.job_id);
      setJobResponse(jobDetails);
      setUploadState(jobDetails.status === 'FAILED' ? 'error' : 'done');
    } catch (err: any) {
      console.error('Upload failed:', err);
      setUploadState('error');
      setErrorMsg(err.message || 'An error occurred during file upload or processing.');
    } finally {
      // Reset input so the same file can be selected again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleReset = () => {
    setUploadState('idle');
    setJobResponse(null);
    setErrorMsg(null);
    setSelectedFileName(null);
    setSelectedFileSize(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={styles.ingestionContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>Multi-CPSE Material Ingestion</h1>
        <p className={styles.subtitle}>Securely upload and validate material master data from participating CPSEs.</p>
      </div>

      <div className={styles.card}>
        <div className={styles.formGroup}>
          <label className={styles.label}>Select Originating CPSE (Optional)</label>
          <select 
            className={styles.select} 
            value={selectedCpse} 
            onChange={(e) => setSelectedCpse(e.target.value)}
            disabled={uploadState !== 'idle'}
          >
            <option value="">-- No CPSE (Auto-detect) --</option>
            <option value="IOCL">IOCL</option>
            <option value="NTPC">NTPC</option>
            <option value="BHEL">BHEL</option>
            <option value="GAIL">GAIL</option>
          </select>
        </div>

        {uploadState === 'idle' && (
          <>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept=".csv,.xlsx" 
              onChange={handleFileSelect} 
            />
            <div className={styles.uploadZone} onClick={handleZoneClick} style={{ cursor: 'pointer' }}>
              <UploadCloud className={styles.uploadIcon} />
              <div className={styles.uploadTitle}>Drop material master file here</div>
              <div className={styles.uploadSubtitle}>or click to browse. Supports CSV and Excel (.xlsx).</div>
              
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
          </>
        )}

        {uploadState !== 'idle' && (
          <div className={styles.stepsContainer}>
            <div className={clsx(styles.step, styles.completed)}>
              <FileSpreadsheet className={styles.stepIcon} />
              <div className={styles.stepContent}>
                <div className={styles.stepTitle}>File Upload</div>
                <div className={styles.stepDesc}>
                  {selectedFileName} {selectedFileSize ? `(${formatFileSize(selectedFileSize)})` : ''}
                </div>
              </div>
              <div className={styles.stepStatus}>Complete</div>
            </div>

            <div className={clsx(styles.step, uploadState === 'uploading' ? styles.active : styles.completed)}>
              {uploadState === 'uploading' ? <Loader2 className={clsx(styles.stepIcon, 'animate-spin')} /> : <CheckCircle2 className={styles.stepIcon} />}
              <div className={styles.stepContent}>
                <div className={styles.stepTitle}>Step 1 → Secure Transfer</div>
                <div className={styles.stepDesc}>Transmitting file to backend processing engine.</div>
              </div>
              <div className={styles.stepStatus}>{uploadState === 'uploading' ? 'Processing...' : 'Complete'}</div>
            </div>

            <div className={clsx(styles.step, uploadState === 'validating' ? styles.active : (uploadState === 'done' || uploadState === 'error' ? styles.completed : ''))}>
              {uploadState === 'validating' ? <Loader2 className={clsx(styles.stepIcon, 'animate-spin')} /> : ((uploadState === 'done' || uploadState === 'error') ? (uploadState === 'error' ? <AlertCircle className={styles.stepIcon} style={{ color: 'red' }}/> : <CheckCircle2 className={styles.stepIcon} />) : <CircleDashed className={styles.stepIcon} />)}
              <div className={styles.stepContent}>
                <div className={styles.stepTitle}>Step 2 → Validation & Processing</div>
                <div className={styles.stepDesc}>Normalizing text, extracting Material DNA, and inserting records.</div>
              </div>
              <div className={styles.stepStatus}>{uploadState === 'validating' ? 'Processing...' : ((uploadState === 'done' || uploadState === 'error') ? 'Complete' : 'Pending')}</div>
            </div>
            
            {(uploadState === 'done' || uploadState === 'error') && jobResponse && (
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ fontSize: '1rem', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  Processing Results
                  <button 
                    onClick={handleReset}
                    style={{ 
                      marginLeft: 'auto', 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '4px', 
                      padding: '4px 8px', 
                      background: 'none', 
                      border: '1px solid #ccc', 
                      borderRadius: '4px', 
                      cursor: 'pointer' 
                    }}
                  >
                    <RefreshCw size={14} /> Upload Another File
                  </button>
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Total Rows</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>{jobResponse.total_rows}</div>
                  </div>
                  <div style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
                    <div style={{ fontSize: '0.75rem', color: '#166534', textTransform: 'uppercase', fontWeight: 600 }}>Accepted</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#15803d' }}>{jobResponse.accepted_rows}</div>
                  </div>
                  <div style={{ background: '#fef2f2', padding: '12px', borderRadius: '8px', border: '1px solid #fecaca' }}>
                    <div style={{ fontSize: '0.75rem', color: '#991b1b', textTransform: 'uppercase', fontWeight: 600 }}>Rejected</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#b91c1c' }}>{jobResponse.rejected_rows}</div>
                  </div>
                  <div style={{ background: '#fffbeb', padding: '12px', borderRadius: '8px', border: '1px solid #fde68a' }}>
                    <div style={{ fontSize: '0.75rem', color: '#b45309', textTransform: 'uppercase', fontWeight: 600 }}>Warnings</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#d97706' }}>{jobResponse.warnings}</div>
                  </div>
                </div>

                {jobResponse.errors && jobResponse.errors.length > 0 && (
                  <div style={{ marginTop: '16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '12px' }}>
                    <h5 style={{ color: '#991b1b', margin: '0 0 8px 0', fontSize: '0.875rem' }}>Validation Errors</h5>
                    <ul style={{ margin: 0, paddingLeft: '20px', color: '#b91c1c', fontSize: '0.875rem' }}>
                      {jobResponse.errors.map((err, i) => (
                        <li key={i}>
                          <strong>Row {err.row}</strong> ({err.field}): {err.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {uploadState === 'error' && errorMsg && (
              <div style={{ marginTop: '16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '12px', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={18} />
                <span style={{ fontSize: '0.875rem' }}>{errorMsg}</span>
                <button 
                  onClick={handleReset}
                  style={{ 
                    marginLeft: 'auto', 
                    padding: '4px 8px', 
                    background: '#fff', 
                    border: '1px solid #fca5a5', 
                    borderRadius: '4px', 
                    cursor: 'pointer',
                    color: '#991b1b'
                  }}
                >
                  Try Again
                </button>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
};

export default Ingestion;
