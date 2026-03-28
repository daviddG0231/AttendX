'use client'

import React, { useState } from 'react'
import { 
  Eye, Users, Camera, Calendar, BarChart3, Bell, Settings,
  ChevronRight, Clock, CheckCircle, XCircle, AlertTriangle,
  Play, Square, UserPlus, FileText, TrendingUp
} from 'lucide-react'

// Mock data for demonstration
const mockDashboardData = {
  stats: {
    totalStudents: 245,
    activeClasses: 3,
    avgAttendance: 87.5,
    facesRegistered: 231
  },
  todaySessions: [
    { id: '1', course: 'CS301 - Machine Learning', room: 'Hall 5A', time: '09:00-10:30', status: 'completed', attendance: 92 },
    { id: '2', course: 'CS205 - Data Structures', room: 'Lab 3B', time: '11:00-12:30', status: 'active', attendance: 85 },
    { id: '3', course: 'CS401 - AI Seminar', room: 'Hall 2C', time: '14:00-15:30', status: 'scheduled', attendance: 0 },
  ],
  recentActivity: [
    { time: '11:23', event: 'Ahmed Sherif recognized in Lab 3B', type: 'entry' },
    { time: '11:21', event: 'Presence check #3 completed for CS205', type: 'check' },
    { time: '11:15', event: 'Mohamed Sheren recognized in Lab 3B', type: 'entry' },
    { time: '11:02', event: 'Spoofing attempt detected in Hall 5A', type: 'alert' },
    { time: '10:30', event: 'CS301 lecture ended - 92% attendance', type: 'complete' },
  ]
}

export default function Dashboard() {
  const [activeSection, setActiveSection] = useState('overview')
  const [user, setUser] = useState<any>(null)
  const data = mockDashboardData

  // Auth check
  React.useEffect(() => {
    const stored = localStorage.getItem('attendx_user')
    if (!stored) {
      window.location.href = '/login'
      return
    }
    const parsed = JSON.parse(stored)
    if (parsed.role !== 'instructor') {
      window.location.href = '/student'
      return
    }
    setUser(parsed)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('attendx_user')
    window.location.href = '/login'
  }

  if (!user) return null
  
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-900/50 border-r border-white/5 p-4 flex flex-col">
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center">
            <Eye className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-lg">AttendX</div>
            <div className="text-xs text-white/40">Instructor Panel</div>
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 space-y-1">
          {[
            { id: 'overview', icon: BarChart3, label: 'Overview' },
            { id: 'sessions', icon: Calendar, label: 'Lecture Sessions' },
            { id: 'students', icon: Users, label: 'Students' },
            { id: 'cameras', icon: Camera, label: 'Cameras' },
            { id: 'reports', icon: FileText, label: 'Reports' },
            { id: 'appeals', icon: AlertTriangle, label: 'Appeals' },
            { id: 'settings', icon: Settings, label: 'Settings' },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={activeSection === item.id ? 'sidebar-link-active w-full' : 'sidebar-link w-full'}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        
        {/* User */}
        <div className="glass-card p-4 mt-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold">
              {user.avatar || 'DG'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user.name}</div>
              <div className="text-xs text-white/40">Instructor</div>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="mt-3 w-full text-xs text-red-400 hover:text-red-300 flex items-center justify-center gap-1.5 py-2 rounded-lg hover:bg-red-500/10 transition-colors"
          >
            <Settings className="w-3 h-3" /> Sign Out
          </button>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-white/40 text-sm mt-1">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button className="btn-secondary flex items-center gap-2 text-sm">
              <Bell className="w-4 h-4" />
              <span className="badge-red">2</span>
            </button>
            <button className="btn-primary flex items-center gap-2 text-sm">
              <Play className="w-4 h-4" />
              Start Session
            </button>
          </div>
        </div>
        
        {/* ============ OVERVIEW ============ */}
        {activeSection === 'overview' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <Users className="w-5 h-5 text-primary-400" />
                  <span className="badge-blue">Active</span>
                </div>
                <div className="text-3xl font-bold">{data.stats.totalStudents}</div>
                <div className="text-sm text-white/40">Total Students</div>
              </div>
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <Camera className="w-5 h-5 text-green-400" />
                  <span className="badge-green">Live</span>
                </div>
                <div className="text-3xl font-bold">{data.stats.activeClasses}</div>
                <div className="text-sm text-white/40">Active Classes</div>
              </div>
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <TrendingUp className="w-5 h-5 text-yellow-400" />
                  <span className="text-xs text-green-400">+2.3%</span>
                </div>
                <div className="text-3xl font-bold">{data.stats.avgAttendance}%</div>
                <div className="text-sm text-white/40">Avg Attendance</div>
              </div>
              <div className="stat-card">
                <div className="flex items-center justify-between">
                  <Eye className="w-5 h-5 text-purple-400" />
                  <span className="text-xs text-white/40">{Math.round(data.stats.facesRegistered / data.stats.totalStudents * 100)}%</span>
                </div>
                <div className="text-3xl font-bold">{data.stats.facesRegistered}</div>
                <div className="text-sm text-white/40">Faces Registered</div>
              </div>
            </div>
            
            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="glass-card">
                  <div className="p-6 border-b border-white/5">
                    <h2 className="text-lg font-semibold">Today&apos;s Sessions</h2>
                  </div>
                  <div className="divide-y divide-white/5">
                    {data.todaySessions.map(session => (
                      <div key={session.id} className="p-6 flex items-center justify-between hover:bg-white/[0.02] transition-colors">
                        <div className="flex items-center gap-4">
                          <div className={`w-3 h-3 rounded-full ${
                            session.status === 'active' ? 'bg-green-500 animate-pulse' :
                            session.status === 'completed' ? 'bg-blue-500' : 'bg-white/20'
                          }`} />
                          <div>
                            <div className="font-medium">{session.course}</div>
                            <div className="text-sm text-white/40 flex items-center gap-2 mt-1">
                              <Clock className="w-3.5 h-3.5" />
                              {session.time} <span>•</span> {session.room}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          {session.status === 'active' && <span className="badge-green">● Live</span>}
                          {session.status === 'completed' && <span className="text-sm text-white/60">{session.attendance}% attendance</span>}
                          {session.status === 'scheduled' && (
                            <button className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1">
                              <Play className="w-3.5 h-3.5" /> Start
                            </button>
                          )}
                          <ChevronRight className="w-4 h-4 text-white/20" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="glass-card">
                <div className="p-6 border-b border-white/5">
                  <h2 className="text-lg font-semibold">Live Activity</h2>
                </div>
                <div className="p-4 space-y-4 max-h-96 overflow-auto">
                  {data.recentActivity.map((activity, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        activity.type === 'entry' ? 'bg-green-500/20' :
                        activity.type === 'check' ? 'bg-blue-500/20' :
                        activity.type === 'alert' ? 'bg-red-500/20' : 'bg-white/10'
                      }`}>
                        {activity.type === 'entry' && <UserPlus className="w-4 h-4 text-green-400" />}
                        {activity.type === 'check' && <CheckCircle className="w-4 h-4 text-blue-400" />}
                        {activity.type === 'alert' && <AlertTriangle className="w-4 h-4 text-red-400" />}
                        {activity.type === 'complete' && <Square className="w-4 h-4 text-white/40" />}
                      </div>
                      <div>
                        <p className="text-sm">{activity.event}</p>
                        <p className="text-xs text-white/30 mt-0.5">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        {/* ============ LECTURE SESSIONS ============ */}
        {activeSection === 'sessions' && (
          <>
            <h2 className="text-xl font-bold mb-6">Lecture Sessions</h2>
            <div className="glass-card">
              <div className="p-4 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <select className="input-field w-auto text-sm">
                    <option>This Week</option>
                    <option>This Month</option>
                    <option>All Time</option>
                  </select>
                </div>
                <button className="btn-primary text-sm flex items-center gap-2">
                  <Play className="w-4 h-4" /> Start New Session
                </button>
              </div>
              <div className="divide-y divide-white/5">
                {[
                  { course: 'CS301 - Machine Learning', room: 'Hall 5A', date: 'Mar 28', time: '09:00-10:30', status: 'completed', attendance: 92, students: 42 },
                  { course: 'CS205 - Data Structures', room: 'Lab 3B', date: 'Mar 28', time: '11:00-12:30', status: 'active', attendance: 85, students: 38 },
                  { course: 'CS401 - AI Seminar', room: 'Hall 2C', date: 'Mar 28', time: '14:00-15:30', status: 'scheduled', attendance: 0, students: 25 },
                  { course: 'CS301 - Machine Learning', room: 'Hall 5A', date: 'Mar 27', time: '09:00-10:30', status: 'completed', attendance: 88, students: 42 },
                  { course: 'CS205 - Data Structures', room: 'Lab 3B', date: 'Mar 27', time: '11:00-12:30', status: 'completed', attendance: 79, students: 38 },
                  { course: 'CS401 - AI Seminar', room: 'Hall 2C', date: 'Mar 26', time: '14:00-15:30', status: 'completed', attendance: 96, students: 25 },
                ].map((s, i) => (
                  <div key={i} className="p-5 flex items-center justify-between hover:bg-white/[0.02] transition-colors">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${
                        s.status === 'active' ? 'bg-green-500 animate-pulse' :
                        s.status === 'completed' ? 'bg-blue-500' : 'bg-white/20'
                      }`} />
                      <div>
                        <div className="font-medium">{s.course}</div>
                        <div className="text-sm text-white/40 flex items-center gap-2 mt-1">
                          <Calendar className="w-3.5 h-3.5" /> {s.date}
                          <span>•</span>
                          <Clock className="w-3.5 h-3.5" /> {s.time}
                          <span>•</span> {s.room}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="text-sm font-medium">{s.attendance}%</div>
                        <div className="text-xs text-white/30">{s.students} students</div>
                      </div>
                      <span className={
                        s.status === 'active' ? 'badge-green' :
                        s.status === 'completed' ? 'badge-blue' : 'badge-yellow'
                      }>
                        {s.status === 'active' ? '● Live' : s.status === 'completed' ? 'Done' : 'Scheduled'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ============ STUDENTS ============ */}
        {activeSection === 'students' && (
          <>
            <h2 className="text-xl font-bold mb-6">Students</h2>
            <div className="glass-card">
              <div className="p-4 border-b border-white/5 flex items-center gap-3">
                <div className="flex-1 relative">
                  <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                  <input className="input-field pl-11 text-sm" placeholder="Search students..." />
                </div>
                <select className="input-field w-auto text-sm">
                  <option>All Courses</option>
                  <option>CS301 - Machine Learning</option>
                  <option>CS205 - Data Structures</option>
                  <option>CS401 - AI Seminar</option>
                </select>
              </div>
              <div className="divide-y divide-white/5">
                {[
                  { name: 'Ahmed Sherif', id: '221017673', course: 'CS301', attendance: 92, face: true },
                  { name: 'Mohamed Sheren', id: '221018445', course: 'CS301', attendance: 88, face: true },
                  { name: 'Sara Hassan', id: '221015592', course: 'CS205', attendance: 71, face: true },
                  { name: 'Omar Khaled', id: '221019201', course: 'CS301', attendance: 40, face: false },
                  { name: 'Nour Ahmed', id: '221016338', course: 'CS401', attendance: 100, face: true },
                  { name: 'Youssef Ibrahim', id: '221017890', course: 'CS205', attendance: 65, face: true },
                  { name: 'Malak Tarek', id: '221014776', course: 'CS401', attendance: 96, face: true },
                  { name: 'David George', id: '221020001', course: 'CS301', attendance: 85, face: true },
                ].map((s, i) => (
                  <div key={i} className="p-5 flex items-center justify-between hover:bg-white/[0.02] transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary-600/30 flex items-center justify-center text-sm font-bold">
                        {s.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div className="font-medium">{s.name}</div>
                        <div className="text-xs text-white/40">{s.id} • {s.course}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className={`text-sm font-semibold ${
                        s.attendance >= 75 ? 'text-green-400' : s.attendance >= 50 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {s.attendance}%
                      </div>
                      {s.face ? (
                        <span className="badge-green">Face ✓</span>
                      ) : (
                        <span className="badge-red">No Face</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ============ CAMERAS ============ */}
        {activeSection === 'cameras' && (
          <>
            <h2 className="text-xl font-bold mb-6">Camera Management</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { name: 'Hall 5A — Main Camera', ip: '192.168.1.100', status: 'online', fps: 30, students: 42 },
                { name: 'Lab 3B — Front Camera', ip: '192.168.1.101', status: 'online', fps: 25, students: 38 },
                { name: 'Hall 2C — Ceiling Camera', ip: '192.168.1.102', status: 'offline', fps: 0, students: 0 },
                { name: 'Lab 1A — Side Camera', ip: '192.168.1.103', status: 'online', fps: 30, students: 0 },
              ].map((cam, i) => (
                <div key={i} className="glass-card p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        cam.status === 'online' ? 'bg-green-500/20' : 'bg-red-500/20'
                      }`}>
                        <Camera className={`w-5 h-5 ${cam.status === 'online' ? 'text-green-400' : 'text-red-400'}`} />
                      </div>
                      <div>
                        <div className="font-medium">{cam.name}</div>
                        <div className="text-xs text-white/40">rtsp://{cam.ip}:554</div>
                      </div>
                    </div>
                    <span className={cam.status === 'online' ? 'badge-green' : 'badge-red'}>
                      {cam.status === 'online' ? '● Online' : '● Offline'}
                    </span>
                  </div>
                  <div className="bg-black/30 rounded-xl aspect-video flex items-center justify-center mb-4">
                    {cam.status === 'online' ? (
                      <div className="text-center">
                        <Camera className="w-8 h-8 text-white/20 mx-auto mb-2" />
                        <p className="text-xs text-white/30">Live feed • {cam.fps} FPS</p>
                      </div>
                    ) : (
                      <p className="text-sm text-red-400/60">Camera offline</p>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/40">{cam.students} students detected</span>
                    {cam.status === 'online' && (
                      <button className="text-primary-400 hover:underline text-xs">View Feed →</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ============ REPORTS ============ */}
        {activeSection === 'reports' && (
          <>
            <h2 className="text-xl font-bold mb-6">Reports</h2>
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {[
                { title: 'Attendance Summary', desc: 'Overall attendance rates per course', icon: FileText, color: 'text-blue-400', bg: 'bg-blue-500/20' },
                { title: 'Student Report', desc: 'Individual student attendance records', icon: Users, color: 'text-green-400', bg: 'bg-green-500/20' },
                { title: 'Low Attendance Alert', desc: 'Students below minimum threshold', icon: AlertTriangle, color: 'text-red-400', bg: 'bg-red-500/20' },
              ].map((report, i) => (
                <div key={i} className="glass-card-hover p-6 cursor-pointer">
                  <div className={`w-12 h-12 rounded-xl ${report.bg} flex items-center justify-center mb-4`}>
                    <report.icon className={`w-6 h-6 ${report.color}`} />
                  </div>
                  <h3 className="font-semibold mb-1">{report.title}</h3>
                  <p className="text-sm text-white/40">{report.desc}</p>
                </div>
              ))}
            </div>
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-4">Course Attendance Summary</h3>
              <div className="space-y-4">
                {[
                  { course: 'CS301 - Machine Learning', rate: 92, sessions: 12, students: 42 },
                  { course: 'CS205 - Data Structures', rate: 79, sessions: 14, students: 38 },
                  { course: 'CS401 - AI Seminar', rate: 96, sessions: 8, students: 25 },
                ].map((c, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{c.course}</span>
                        <span className={`text-sm font-bold ${c.rate >= 85 ? 'text-green-400' : c.rate >= 70 ? 'text-yellow-400' : 'text-red-400'}`}>{c.rate}%</span>
                      </div>
                      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${c.rate >= 85 ? 'bg-green-500' : c.rate >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${c.rate}%` }} />
                      </div>
                      <div className="text-xs text-white/30 mt-1">{c.sessions} sessions • {c.students} students</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ============ APPEALS ============ */}
        {activeSection === 'appeals' && (
          <>
            <h2 className="text-xl font-bold mb-6">Attendance Appeals</h2>
            <div className="glass-card">
              <div className="divide-y divide-white/5">
                {[
                  { student: 'Omar Khaled', id: '221019201', course: 'CS301', date: 'Mar 27', reason: 'Was present but camera did not detect me — sat in the back row', status: 'pending' },
                  { student: 'Sara Hassan', id: '221015592', course: 'CS205', date: 'Mar 26', reason: 'Medical appointment — doctor note attached', status: 'pending' },
                  { student: 'Youssef Ibrahim', id: '221017890', course: 'CS205', date: 'Mar 25', reason: 'Face registration was not complete at the time', status: 'approved' },
                  { student: 'Malak Tarek', id: '221014776', course: 'CS401', date: 'Mar 24', reason: 'Internet connection issue during online lecture', status: 'rejected' },
                ].map((appeal, i) => (
                  <div key={i} className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary-600/30 flex items-center justify-center text-sm font-bold">
                          {appeal.student.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <div className="font-medium">{appeal.student}</div>
                          <div className="text-xs text-white/40">{appeal.id} • {appeal.course} • {appeal.date}</div>
                        </div>
                      </div>
                      <span className={
                        appeal.status === 'pending' ? 'badge-yellow' :
                        appeal.status === 'approved' ? 'badge-green' : 'badge-red'
                      }>
                        {appeal.status}
                      </span>
                    </div>
                    <p className="text-sm text-white/60 ml-13 pl-13">&ldquo;{appeal.reason}&rdquo;</p>
                    {appeal.status === 'pending' && (
                      <div className="flex items-center gap-3 mt-4 ml-13 pl-13">
                        <button className="btn-primary text-xs px-4 py-2 flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" /> Approve
                        </button>
                        <button className="btn-danger text-xs px-4 py-2 flex items-center gap-1">
                          <XCircle className="w-3.5 h-3.5" /> Reject
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ============ SETTINGS ============ */}
        {activeSection === 'settings' && (
          <>
            <h2 className="text-xl font-bold mb-6">Settings</h2>
            <div className="max-w-2xl space-y-6">
              <div className="glass-card p-6">
                <h3 className="font-semibold mb-4">Recognition Settings</h3>
                <div className="space-y-4">
                  {[
                    { label: 'Confidence Threshold', value: '85%', desc: 'Minimum confidence for positive match' },
                    { label: 'Anti-Spoofing', value: 'Enabled', desc: 'Reject photos/video of faces' },
                    { label: 'Periodic Check Interval', value: '15 min', desc: 'Time between presence verifications' },
                    { label: 'Late Threshold', value: '10 min', desc: 'Minutes after which entry counts as late' },
                  ].map((setting, i) => (
                    <div key={i} className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
                      <div>
                        <div className="text-sm font-medium">{setting.label}</div>
                        <div className="text-xs text-white/30">{setting.desc}</div>
                      </div>
                      <span className="text-sm text-primary-400 font-medium">{setting.value}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="glass-card p-6">
                <h3 className="font-semibold mb-4">Profile</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-3 border-b border-white/5">
                    <span className="text-sm text-white/50">Name</span>
                    <span className="text-sm font-medium">{user?.name || 'Instructor'}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-white/5">
                    <span className="text-sm text-white/50">Email</span>
                    <span className="text-sm font-medium">{user?.email || 'instructor@example.com'}</span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-sm text-white/50">Role</span>
                    <span className="badge-blue">Instructor</span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
