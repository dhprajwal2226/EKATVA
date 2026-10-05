import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './layouts/AppLayout';
import Login from './pages/Login';
import Overview from './pages/Overview';
import Ingestion from './pages/Ingestion';
import MaterialDNA from './pages/MaterialDNA';
import AIMatching from './pages/AIMatching';
import Validation from './pages/Validation';
import NationalMaster from './pages/NationalMaster';
import Normalization from './pages/Normalization';
import MaterialGraph from './pages/MaterialGraph';
import IntelligenceMap from './pages/IntelligenceMap';
import Procurement from './pages/Procurement';
import Passport from './pages/Passport';
import Copilot from './pages/Copilot';
import { useEffect } from 'react';
import { getHealth } from './services/health';

function App() {
  useEffect(() => {
    // Development-only health check to verify React -> API Client -> FastAPI -> Database
    if (import.meta.env.DEV) {
      getHealth()
        .then(response => {
          console.log('%c[EKATVA API Health Check] Success:', 'color: green; font-weight: bold;', response);
        })
        .catch(error => {
          console.error('%c[EKATVA API Health Check] Failed:', 'color: red; font-weight: bold;', error);
        });
    }
  }, []);

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<Navigate to="/overview" replace />} />
              <Route path="overview" element={<Overview />} />
              <Route path="ingestion" element={<Ingestion />} />
              <Route path="dna" element={<MaterialDNA />} />
              <Route path="matching" element={<AIMatching />} />
              <Route path="validation" element={<Validation />} />
              <Route path="master" element={<NationalMaster />} />
              <Route path="normalization" element={<Normalization />} />
              <Route path="graph" element={<MaterialGraph />} />
              <Route path="map" element={<IntelligenceMap />} />
              <Route path="procurement" element={<Procurement />} />
              <Route path="passport" element={<Passport />} />
              <Route path="copilot" element={<Copilot />} />
              <Route path="*" element={<div style={{ padding: '24px' }}>Page under construction</div>} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
