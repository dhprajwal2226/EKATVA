import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute() {
  const { token, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (!token || !user) return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}
