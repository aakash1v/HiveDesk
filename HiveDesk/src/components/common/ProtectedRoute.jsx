import React from 'react'
import { Navigate } from 'react-router-dom'

const ProtectedRoute = ({ children, role }) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn')
  const userRole = localStorage.getItem('userRole')

  if (!isLoggedIn) {
    return <Navigate to="/login" />
  }

  if (role && userRole !== role) {
    return <Navigate to={userRole === 'hr' ? '/hr-dashboard' : '/employee-dashboard'} />
  }

  return children
}

export default ProtectedRoute