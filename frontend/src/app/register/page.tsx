'use client'

import { useState } from 'react'
import { Eye, Mail, Lock, User, Hash, ArrowRight, ArrowLeft } from 'lucide-react'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    studentId: '',
    password: '',
    confirmPassword: '',
    department: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    try {
      const res = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          full_name: formData.fullName,
          role: 'student',
          student_id: formData.studentId,
          department: formData.department
        })
      })

      const data = await res.json()

      if (data.success) {
        // Redirect to face registration
        window.location.href = `/student/face-register?id=${formData.studentId}&name=${encodeURIComponent(formData.fullName)}`
      } else {
        setError(data.detail || 'Registration failed')
      }
    } catch (err) {
      setError('Server error. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center mx-auto mb-4">
            <Eye className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold">Create Account</h1>
          <p className="text-white/40 mt-2">Register to start using AttendX</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Full Name */}
          <div>
            <label className="text-sm text-white/60 mb-2 block">Full Name</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="text"
                className="input-field pl-11"
                placeholder="Ahmed Sherif"
                value={formData.fullName}
                onChange={e => setFormData({...formData, fullName: e.target.value})}
                required
              />
            </div>
          </div>

          {/* Student ID */}
          <div>
            <label className="text-sm text-white/60 mb-2 block">Student ID</label>
            <div className="relative">
              <Hash className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="text"
                className="input-field pl-11"
                placeholder="221017673"
                value={formData.studentId}
                onChange={e => setFormData({...formData, studentId: e.target.value})}
                required
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="text-sm text-white/60 mb-2 block">University Email</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="email"
                className="input-field pl-11"
                placeholder="ahmed@student.aast.edu"
                value={formData.email}
                onChange={e => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
          </div>

          {/* Department */}
          <div>
            <label className="text-sm text-white/60 mb-2 block">Department</label>
            <select
              className="input-field"
              value={formData.department}
              onChange={e => setFormData({...formData, department: e.target.value})}
              required
            >
              <option value="">Select department</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Software Engineering">Software Engineering</option>
              <option value="AI & Data Science">AI & Data Science</option>
              <option value="Information Systems">Information Systems</option>
              <option value="Networking">Networking</option>
            </select>
          </div>

          {/* Password */}
          <div>
            <label className="text-sm text-white/60 mb-2 block">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="password"
                className="input-field pl-11"
                placeholder="••••••••"
                value={formData.password}
                onChange={e => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="text-sm text-white/60 mb-2 block">Confirm Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="password"
                className="input-field pl-11"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={e => setFormData({...formData, confirmPassword: e.target.value})}
                required
              />
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2 py-3"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                Create Account <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>

          {/* Steps indicator */}
          <div className="flex items-center justify-center gap-2 pt-2">
            <div className="w-8 h-1 rounded-full bg-primary-500" />
            <div className="w-8 h-1 rounded-full bg-white/10" />
            <div className="w-8 h-1 rounded-full bg-white/10" />
            <span className="text-xs text-white/30 ml-2">Step 1 of 3</span>
          </div>

          <p className="text-center text-sm text-white/30">
            Already have an account? <a href="/login" className="text-primary-400 hover:underline">Sign in</a>
          </p>
        </form>
      </div>
    </div>
  )
}
