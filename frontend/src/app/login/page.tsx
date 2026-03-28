'use client'

import { useState } from 'react'
import { Eye, Mail, Lock, ArrowRight } from 'lucide-react'

// Demo accounts
const DEMO_ACCOUNTS = [
  {
    email: 'david@teacher.com',
    password: 'David123',
    user: {
      name: 'David George',
      email: 'david@teacher.com',
      role: 'instructor',
      avatar: 'DG',
    }
  },
  {
    email: 'david@student.com',
    password: 'David123',
    user: {
      name: 'David George',
      email: 'david@student.com',
      role: 'student',
      studentId: '221017673',
      department: 'AI & Data Analytics',
      avatar: 'DG',
    }
  }
]

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Simulate network delay
    await new Promise(r => setTimeout(r, 600))

    const account = DEMO_ACCOUNTS.find(
      a => a.email === email.toLowerCase().trim() && a.password === password
    )

    if (account) {
      localStorage.setItem('attendx_user', JSON.stringify(account.user))
      
      if (account.user.role === 'instructor') {
        window.location.href = '/dashboard'
      } else {
        window.location.href = '/student'
      }
    } else {
      setError('Invalid email or password. Try david@teacher.com or david@student.com with David123')
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center mx-auto mb-4">
            <Eye className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold">Welcome Back</h1>
          <p className="text-white/40 mt-2">Sign in to AttendX</p>
        </div>

        <form onSubmit={handleSubmit} className="glass-card p-8 space-y-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="text-sm text-white/60 mb-2 block">Email</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="email"
                className="input-field pl-11"
                placeholder="david@teacher.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <label className="text-sm text-white/60 mb-2 block">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
              <input
                type="password"
                className="input-field pl-11"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2 py-3"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>Sign In <ArrowRight className="w-4 h-4" /></>
            )}
          </button>

          {/* Demo accounts hint */}
          <div className="pt-2 border-t border-white/5">
            <p className="text-xs text-white/30 text-center mb-3">Demo Accounts</p>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => { setEmail('david@teacher.com'); setPassword('David123') }}
                className="w-full text-left bg-white/5 hover:bg-white/10 rounded-lg px-3 py-2 text-xs transition-colors"
              >
                <span className="text-primary-400 font-medium">Instructor:</span>
                <span className="text-white/50 ml-2">david@teacher.com / David123</span>
              </button>
              <button
                type="button"
                onClick={() => { setEmail('david@student.com'); setPassword('David123') }}
                className="w-full text-left bg-white/5 hover:bg-white/10 rounded-lg px-3 py-2 text-xs transition-colors"
              >
                <span className="text-green-400 font-medium">Student:</span>
                <span className="text-white/50 ml-2">david@student.com / David123</span>
              </button>
            </div>
          </div>

          <p className="text-center text-sm text-white/30">
            Don&apos;t have an account? <a href="/register" className="text-primary-400 hover:underline">Register</a>
          </p>
        </form>
      </div>
    </div>
  )
}
