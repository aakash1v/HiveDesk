import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth } from '../services/firebaseConfig'
import toast from 'react-hot-toast'

const LoginPage = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const userCredential = await signInWithEmailAndPassword(
        auth,
        email,
        password
      )

      const userEmail = userCredential.user.email

      // SIMPLE ROLE LOGIC (SAFE FOR DEMO)
      if (userEmail.includes('hr')) {
        localStorage.setItem('role', 'hr')
        navigate('/hr-dashboard')
      } else {
        localStorage.setItem('role', 'employee')
        navigate('/employee-dashboard')
      }

      toast.success('Login successful!')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-blue-600 to-purple-700 flex items-center justify-center px-4">
      <div className="w-full max-w-4xl bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl overflow-hidden grid grid-cols-1 md:grid-cols-2">

        {/* Left Branding Section */}
        <div className="hidden md:flex flex-col justify-center p-10 text-white">
          <h1 className="text-4xl font-bold mb-4">
            Intelligent HR Onboarding
          </h1>
          <p className="text-lg text-white/80">
            Automate onboarding, verify documents with AI, and deliver
            personalized employee experiences.
          </p>

          <div className="mt-8 space-y-3 text-sm text-white/70">
            <p>✔ AI-powered document verification</p>
            <p>✔ Automated task assignment</p>
            <p>✔ Role-based onboarding</p>
          </div>
        </div>

        {/* Right Login Form */}
        <div className="bg-white p-8 md:p-10">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Welcome Back
          </h2>
          <p className="text-sm text-gray-500 mb-6">
            Sign in to continue to your dashboard
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-600">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="you@company.com"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium text-gray-600">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-2.5 rounded-lg font-semibold hover:opacity-90 transition disabled:opacity-60"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 text-sm text-center text-gray-500">
            Demo Access
            <div className="flex justify-center gap-4 mt-3">
              <button
                onClick={() => {
                  setEmail('hr@company.com')
                  setPassword('password')
                }}
                className="px-4 py-1.5 border rounded-full text-blue-600 hover:bg-blue-50"
              >
                HR Login
              </button>

              <button
                onClick={() => {
                  setEmail('employee@company.com')
                  setPassword('password')
                }}
                className="px-4 py-1.5 border rounded-full text-purple-600 hover:bg-purple-50"
              >
                Employee Login
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default LoginPage
