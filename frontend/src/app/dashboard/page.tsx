'use client'

import { useState } from 'react'
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
  const data = mockDashboardData
  
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
              AG
            </div>
            <div>
              <div className="text-sm font-medium">Prof. Atef G.</div>
              <div className="text-xs text-white/40">Instructor</div>
            </div>
          </div>
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
        
        {/* Stats Grid */}
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
          {/* Today's Sessions */}
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
                          {session.time}
                          <span>•</span>
                          {session.room}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {session.status === 'active' && (
                        <span className="badge-green">● Live</span>
                      )}
                      {session.status === 'completed' && (
                        <span className="text-sm text-white/60">{session.attendance}% attendance</span>
                      )}
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
          
          {/* Activity Feed */}
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
                    activity.type === 'alert' ? 'bg-red-500/20' :
                    'bg-white/10'
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
      </main>
    </div>
  )
}
