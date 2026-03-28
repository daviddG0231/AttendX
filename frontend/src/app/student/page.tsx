'use client'

import React, { useState, useEffect } from 'react'
import {
  Eye, User, BookOpen, Calendar, CheckCircle, XCircle,
  Camera, BarChart3, Bell, Settings, LogOut, Clock,
  TrendingUp, TrendingDown, AlertTriangle, ChevronRight
} from 'lucide-react'

// Default mock student (overridden by logged-in user)
const defaultStudent = {
  name: 'Student',
  studentId: '000000000',
  email: 'student@example.com',
  department: 'Unknown',
  isFaceRegistered: false,
  avatar: 'ST'
}

const mockCourses = [
  {
    id: '1',
    code: 'CS301',
    name: 'Machine Learning',
    instructor: 'Prof. Atef Ghalwsh',
    totalSessions: 12,
    attended: 11,
    rate: 91.7,
    status: 'good'
  },
  {
    id: '2', 
    code: 'CS205',
    name: 'Data Structures',
    instructor: 'Dr. Mohamed Ali',
    totalSessions: 14,
    attended: 10,
    rate: 71.4,
    status: 'warning'
  },
  {
    id: '3',
    code: 'CS401',
    name: 'AI Seminar',
    instructor: 'Prof. Atef Ghalwsh',
    totalSessions: 8,
    attended: 8,
    rate: 100,
    status: 'good'
  },
  {
    id: '4',
    code: 'CS102',
    name: 'Operating Systems',
    instructor: 'Dr. Sara Ahmed',
    totalSessions: 10,
    attended: 4,
    rate: 40,
    status: 'critical'
  }
]

const mockRecentAttendance = [
  { date: '2026-03-27', course: 'CS301 - Machine Learning', status: 'present', time: '09:03', presence: 95 },
  { date: '2026-03-27', course: 'CS205 - Data Structures', status: 'present', time: '11:01', presence: 88 },
  { date: '2026-03-26', course: 'CS401 - AI Seminar', status: 'present', time: '14:00', presence: 100 },
  { date: '2026-03-26', course: 'CS102 - Operating Systems', status: 'absent', time: '-', presence: 0 },
  { date: '2026-03-25', course: 'CS301 - Machine Learning', status: 'present', time: '09:05', presence: 92 },
  { date: '2026-03-25', course: 'CS205 - Data Structures', status: 'late', time: '11:18', presence: 65 },
  { date: '2026-03-24', course: 'CS401 - AI Seminar', status: 'present', time: '13:58', presence: 100 },
  { date: '2026-03-24', course: 'CS102 - Operating Systems', status: 'absent', time: '-', presence: 0 },
]

export default function StudentDashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [user, setUser] = useState<any>(null)
  const [facePhotos, setFacePhotos] = useState<string[]>([])
  
  useEffect(() => {
    const stored = localStorage.getItem('attendx_user')
    if (!stored) {
      window.location.href = '/login'
      return
    }
    const parsed = JSON.parse(stored)
    if (parsed.role !== 'student') {
      window.location.href = '/dashboard'
      return
    }
    setUser(parsed)
    
    // Load face photos from localStorage
    const photos = localStorage.getItem('attendx_face_photos')
    if (photos) setFacePhotos(JSON.parse(photos))
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('attendx_user')
    window.location.href = '/login'
  }

  if (!user) return null

  const student = {
    ...defaultStudent,
    name: user.name || defaultStudent.name,
    email: user.email || defaultStudent.email,
    studentId: user.studentId || defaultStudent.studentId,
    department: user.department || defaultStudent.department,
    avatar: user.avatar || defaultStudent.avatar,
    isFaceRegistered: facePhotos.length >= 5,
  }

  const courses = mockCourses
  const overall = Math.round(courses.reduce((sum, c) => sum + c.rate, 0) / courses.length)

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-900/50 border-r border-white/5 p-4 flex flex-col">
        <div className="flex items-center gap-3 px-4 py-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center">
            <Eye className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-lg">AttendX</div>
            <div className="text-xs text-white/40">Student Portal</div>
          </div>
        </div>

        <nav className="flex-1 space-y-1">
          {[
            { id: 'overview', icon: BarChart3, label: 'Overview' },
            { id: 'courses', icon: BookOpen, label: 'My Courses' },
            { id: 'history', icon: Calendar, label: 'Attendance History' },
            { id: 'face', icon: Camera, label: 'Face Settings' },
            { id: 'profile', icon: User, label: 'Profile' },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={activeTab === item.id ? 'sidebar-link-active w-full' : 'sidebar-link w-full'}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Student Info */}
        <div className="glass-card p-4 mt-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-sm font-bold">
              {student.avatar}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{student.name}</div>
              <div className="text-xs text-white/40">{student.studentId}</div>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="mt-3 w-full text-xs text-red-400 hover:text-red-300 flex items-center justify-center gap-1.5 py-2 rounded-lg hover:bg-red-500/10 transition-colors"
          >
            <LogOut className="w-3 h-3" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            <div className="mb-8">
              <h1 className="text-2xl font-bold">Welcome back, {student.name.split(' ')[0]}! 👋</h1>
              <p className="text-white/40 text-sm mt-1">Here&apos;s your attendance overview</p>
            </div>

            {/* Alerts */}
            {courses.filter(c => c.status === 'critical').length > 0 && (
              <div className="mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-medium text-red-400">Low Attendance Warning</p>
                  <p className="text-sm text-white/50 mt-1">
                    Your attendance in {courses.filter(c => c.status === 'critical').map(c => c.name).join(', ')} is 
                    below 50%. You may be at risk of failing the attendance requirement.
                  </p>
                </div>
              </div>
            )}

            {/* Face registration status */}
            {!student.isFaceRegistered && (
              <div className="mb-6 bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Camera className="w-5 h-5 text-yellow-400" />
                  <div>
                    <p className="font-medium text-yellow-400">Face not registered</p>
                    <p className="text-sm text-white/50">Register your face to start automatic attendance</p>
                  </div>
                </div>
                <a href="/student/face-register" className="btn-primary text-sm">Register Now</a>
              </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <BarChart3 className="w-5 h-5 text-primary-400" />
                  {overall >= 75 ? (
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-400" />
                  )}
                </div>
                <div className="text-3xl font-bold">{overall}%</div>
                <div className="text-sm text-white/40">Overall Attendance</div>
              </div>

              <div className="stat-card">
                <BookOpen className="w-5 h-5 text-blue-400" />
                <div className="text-3xl font-bold">{courses.length}</div>
                <div className="text-sm text-white/40">Enrolled Courses</div>
              </div>

              <div className="stat-card">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <div className="text-3xl font-bold">{courses.reduce((s, c) => s + c.attended, 0)}</div>
                <div className="text-sm text-white/40">Sessions Attended</div>
              </div>

              <div className="stat-card">
                <XCircle className="w-5 h-5 text-red-400" />
                <div className="text-3xl font-bold">
                  {courses.reduce((s, c) => s + (c.totalSessions - c.attended), 0)}
                </div>
                <div className="text-sm text-white/40">Sessions Missed</div>
              </div>
            </div>

            {/* Course Cards */}
            <h2 className="text-lg font-semibold mb-4">Course Attendance</h2>
            <div className="grid md:grid-cols-2 gap-4 mb-8">
              {courses.map(course => (
                <div key={course.id} className="glass-card p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <span className="text-xs text-white/40">{course.code}</span>
                      <h3 className="font-medium">{course.name}</h3>
                      <p className="text-xs text-white/30 mt-1">{course.instructor}</p>
                    </div>
                    <span className={
                      course.status === 'good' ? 'badge-green' :
                      course.status === 'warning' ? 'badge-yellow' : 'badge-red'
                    }>
                      {course.rate}%
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-2">
                    <div
                      className={`h-full rounded-full transition-all ${
                        course.status === 'good' ? 'bg-green-500' :
                        course.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${course.rate}%` }}
                    />
                  </div>

                  <div className="flex justify-between text-xs text-white/40">
                    <span>{course.attended}/{course.totalSessions} sessions</span>
                    <span>{course.totalSessions - course.attended} missed</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Attendance */}
            <h2 className="text-lg font-semibold mb-4">Recent Attendance</h2>
            <div className="glass-card">
              <div className="divide-y divide-white/5">
                {mockRecentAttendance.slice(0, 6).map((record, i) => (
                  <div key={i} className="px-6 py-4 flex items-center justify-between hover:bg-white/[0.02]">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        record.status === 'present' ? 'bg-green-500/20' :
                        record.status === 'late' ? 'bg-yellow-500/20' : 'bg-red-500/20'
                      }`}>
                        {record.status === 'present' ? <CheckCircle className="w-5 h-5 text-green-400" /> :
                         record.status === 'late' ? <Clock className="w-5 h-5 text-yellow-400" /> :
                         <XCircle className="w-5 h-5 text-red-400" />}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{record.course}</p>
                        <p className="text-xs text-white/30">{record.date} • Entry: {record.time}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={
                        record.status === 'present' ? 'badge-green' :
                        record.status === 'late' ? 'badge-yellow' : 'badge-red'
                      }>
                        {record.status === 'present' ? 'Present' :
                         record.status === 'late' ? 'Late' : 'Absent'}
                      </span>
                      {record.presence > 0 && (
                        <p className="text-xs text-white/30 mt-1">{record.presence}% presence</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <>
            <h1 className="text-2xl font-bold mb-6">My Courses</h1>
            <div className="space-y-4">
              {courses.map(course => (
                <div key={course.id} className="glass-card p-6 flex items-center justify-between">
                  <div className="flex items-center gap-6">
                    <div className="w-14 h-14 rounded-xl bg-primary-500/20 flex items-center justify-center">
                      <BookOpen className="w-6 h-6 text-primary-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{course.code} — {course.name}</h3>
                      <p className="text-sm text-white/40">{course.instructor}</p>
                      <p className="text-xs text-white/30 mt-1">
                        {course.attended}/{course.totalSessions} sessions attended
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${
                      course.rate >= 75 ? 'text-green-400' :
                      course.rate >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {course.rate}%
                    </div>
                    <span className={
                      course.status === 'good' ? 'badge-green' :
                      course.status === 'warning' ? 'badge-yellow' : 'badge-red'
                    }>
                      {course.status === 'good' ? '✓ Good' :
                       course.status === 'warning' ? '⚠ Warning' : '✕ Critical'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <>
            <h1 className="text-2xl font-bold mb-6">Attendance History</h1>
            <div className="glass-card">
              <div className="p-4 border-b border-white/5 flex items-center gap-4">
                <select className="input-field w-auto text-sm">
                  <option>All Courses</option>
                  {courses.map(c => <option key={c.id}>{c.code} - {c.name}</option>)}
                </select>
                <select className="input-field w-auto text-sm">
                  <option>All Status</option>
                  <option>Present</option>
                  <option>Late</option>
                  <option>Absent</option>
                </select>
              </div>
              <div className="divide-y divide-white/5">
                {mockRecentAttendance.map((record, i) => (
                  <div key={i} className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${
                        record.status === 'present' ? 'bg-green-500' :
                        record.status === 'late' ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                      <div>
                        <p className="font-medium text-sm">{record.course}</p>
                        <p className="text-xs text-white/30">{record.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <span className="text-sm text-white/40">Entry: {record.time}</span>
                      <span className="text-sm text-white/40">{record.presence}%</span>
                      <span className={`w-20 text-center ${
                        record.status === 'present' ? 'badge-green' :
                        record.status === 'late' ? 'badge-yellow' : 'badge-red'
                      }`}>
                        {record.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Face Settings Tab */}
        {activeTab === 'face' && (
          <>
            <h1 className="text-2xl font-bold mb-6">Face Recognition Settings</h1>
            <div className="glass-card p-6 max-w-xl">
              <div className="flex items-center gap-4 mb-6">
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center ${
                  student.isFaceRegistered ? 'bg-green-500/20' : 'bg-red-500/20'
                }`}>
                  {student.isFaceRegistered ? 
                    <CheckCircle className="w-7 h-7 text-green-400" /> :
                    <XCircle className="w-7 h-7 text-red-400" />
                  }
                </div>
                <div>
                  <h3 className="font-semibold">
                    {student.isFaceRegistered ? 'Face Registered ✓' : 'Face Not Registered'}
                  </h3>
                  <p className="text-sm text-white/40">
                    {student.isFaceRegistered 
                      ? 'Your face is registered and active for attendance' 
                      : 'Register your face to enable automatic attendance'}
                  </p>
                </div>
              </div>

              {student.isFaceRegistered ? (
                <div className="space-y-4">
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/50">Status</span>
                      <span className="text-green-400">Active</span>
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/50">Photos registered</span>
                      <span>5</span>
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-xl p-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/50">Last updated</span>
                      <span>March 27, 2026</span>
                    </div>
                  </div>
                  <a href="/student/face-register" className="btn-secondary w-full text-center block">
                    Re-register Face Photos
                  </a>
                </div>
              ) : (
                <a href="/student/face-register" className="btn-primary w-full text-center block">
                  Register Face Now
                </a>
              )}
            </div>
          </>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <>
            <h1 className="text-2xl font-bold mb-6">My Profile</h1>
            <div className="glass-card p-6 max-w-xl">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-2xl font-bold">
                  {student.avatar}
                </div>
                <div>
                  <h2 className="text-xl font-bold">{student.name}</h2>
                  <p className="text-white/40">{student.department}</p>
                </div>
              </div>
              
              <div className="space-y-4">
                {[
                  { label: 'Student ID', value: student.studentId },
                  { label: 'Email', value: student.email },
                  { label: 'Department', value: student.department },
                  { label: 'Face Status', value: student.isFaceRegistered ? '✅ Registered' : '❌ Not registered' },
                  { label: 'Overall Attendance', value: `${overall}%` },
                ].map((item, i) => (
                  <div key={i} className="bg-white/5 rounded-xl p-4 flex justify-between">
                    <span className="text-white/50">{item.label}</span>
                    <span className="font-medium">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
