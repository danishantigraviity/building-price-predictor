import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import { useAuth } from './context/AuthContext';

// Lazy Load Pages
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Estimate = lazy(() => import('./pages/Estimate'));
const Result = lazy(() => import('./pages/Result'));
const Profile = lazy(() => import('./pages/Profile'));
const Admin = lazy(() => import('./pages/Admin'));
import ErrorBoundary from './components/ErrorBoundary'
import Background3D from './components/Background3D';

function App() {
  const { user, loading } = useAuth();

  if (loading) return <div className="d-flex justify-content-center align-items-center vh-100"><div className="spinner-border text-primary" role="status"></div></div>;

  return (
    <Router>
      <Background3D>
        <Navbar />
        <div className="container mt-4 min-vh-100">
          <Suspense fallback={<div className="d-flex justify-content-center align-items-center vh-100"><div className="spinner-border text-primary"></div></div>}>
            <Routes>
              <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
              <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" />} />

              <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
              <Route path="/estimate" element={<PrivateRoute><Estimate /></PrivateRoute>} />
              <Route path="/result/:id" element={<PrivateRoute><Result /></PrivateRoute>} />
              <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
              <Route path="/admin" element={<PrivateRoute adminOnly><Admin /></PrivateRoute>} />

              <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
            </Routes>
          </Suspense>
        </div>
      </Background3D>
    </Router>
  );
}

export default App;
