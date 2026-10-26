import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Login from './pages/auth/login/Login';
import AdminDashboard from './pages/admin/dashboard/Dashboard';
import WarehouseDashboard from './pages/warehouse/dashboard/Dashboard';

const ProtectedRoute = ({ element, allowedRole }) => {
  const currentRole = localStorage.getItem('userRole');
  const accessToken = localStorage.getItem('accessToken');
  if (!accessToken || currentRole !== allowedRole) {
    return <Navigate to="/login" replace />;
  }
  return element;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/admin" element={<ProtectedRoute allowedRole="admin" element={<AdminDashboard />} />} />
        <Route path="/warehouse" element={<ProtectedRoute allowedRole="warehouse_staff" element={<WarehouseDashboard />} />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
