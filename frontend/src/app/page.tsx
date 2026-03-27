'use client'

import { useState } from 'react'
import { Eye, Users, Camera, Shield, ArrowRight, CheckCircle, Zap, BarChart3 } from 'lucide-react'

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState<'student' | 'instructor'>('instructor')
  
  return (
    <div className="min-h-screen bg-dark-950">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-dark-950/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center">
              <Eye className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">AttendX</span>
          </div>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-white/60 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-white/60 hover:text-white transition-colors">How It Works</a>
            <a href="#tech" className="text-white/60 hover:text-white transition-colors">Technology</a>
          </div>
          
          <div className="flex items-center gap-3">
            <a href="/login" className="btn-secondary text-sm">Sign In</a>
            <a href="/register" className="btn-primary text-sm">Get Started</a>
          </div>
        </div>
      </nav>
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/20 rounded-full px-4 py-1.5 mb-8">
            <Zap className="w-4 h-4 text-primary-400" />
            <span className="text-sm text-primary-300">AI-Powered Attendance System</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Attendance Made
            <span className="bg-gradient-to-r from-primary-400 to-blue-400 bg-clip-text text-transparent"> Intelligent</span>
          </h1>
          
          <p className="text-xl text-white/50 max-w-2xl mx-auto mb-12">
            Automatically record student attendance using AI facial recognition. 
            No manual roll calls, no QR codes, no interruptions. Just smart, 
            accurate attendance tracking.
          </p>
          
          <div className="flex items-center justify-center gap-4">
            <a href="/dashboard" className="btn-primary text-lg px-8 py-4 flex items-center gap-2">
              Open Dashboard <ArrowRight className="w-5 h-5" />
            </a>
            <a href="#how-it-works" className="btn-secondary text-lg px-8 py-4">
              Learn More
            </a>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-4xl mx-auto">
            {[
              { value: '90%+', label: 'Recognition Accuracy', icon: Eye },
              { value: '1-3s', label: 'Recognition Speed', icon: Zap },
              { value: '99%', label: 'System Uptime', icon: Shield },
              { value: '30+', label: 'Students Per Class', icon: Users },
            ].map((stat, i) => (
              <div key={i} className="glass-card p-6 text-center">
                <stat.icon className="w-6 h-6 text-primary-400 mx-auto mb-3" />
                <div className="text-3xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-white/40">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-white/50 max-w-xl mx-auto">
              Everything you need for modern, automated attendance management
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Eye,
                title: 'Real-Time Recognition',
                description: 'AI-powered facial recognition processes live camera feeds to identify students automatically as they enter the classroom.',
                color: 'from-blue-500 to-cyan-500'
              },
              {
                icon: Camera,
                title: 'RTSP Camera Integration',
                description: 'Connect any IP camera via RTSP protocol. Works with existing university infrastructure — no special hardware needed.',
                color: 'from-purple-500 to-pink-500'
              },
              {
                icon: Shield,
                title: 'Anti-Spoofing Protection',
                description: 'Advanced liveness detection prevents cheating with photos or video replays. Only real, live faces are accepted.',
                color: 'from-orange-500 to-red-500'
              },
              {
                icon: BarChart3,
                title: 'Instructor Dashboard',
                description: 'Comprehensive dashboard for viewing attendance records, monitoring sessions, managing appeals, and generating reports.',
                color: 'from-green-500 to-emerald-500'
              },
              {
                icon: Users,
                title: 'Periodic Verification',
                description: 'Not just entry detection — periodic checks throughout the lecture ensure students remain present for the full duration.',
                color: 'from-yellow-500 to-orange-500'
              },
              {
                icon: CheckCircle,
                title: 'Smart Scheduling',
                description: 'Integrates with lecture schedules to automatically activate monitoring at the right time and place.',
                color: 'from-pink-500 to-rose-500'
              }
            ].map((feature, i) => (
              <div key={i} className="glass-card-hover p-8">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-white/50 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-6 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-white/50 max-w-xl mx-auto">
              Three simple steps to fully automated attendance
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-12">
            {[
              {
                step: '01',
                title: 'Register Faces',
                description: 'Students register their facial data through the secure portal with minimum 5 photos under different conditions.'
              },
              {
                step: '02',
                title: 'Automatic Detection',
                description: 'Cameras detect and identify students as they enter. Periodic checks verify continued presence throughout the lecture.'
              },
              {
                step: '03',
                title: 'View Records',
                description: 'Instructors access real-time dashboards with attendance records, analytics, and the ability to manage appeals.'
              }
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="text-6xl font-bold text-primary-500/20 mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                <p className="text-white/50">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Tech Stack */}
      <section id="tech" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Technology Stack</h2>
            <p className="text-white/50 max-w-xl mx-auto">
              Built with industry-leading AI and web technologies
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'RetinaFace', desc: 'Face Detection' },
              { name: 'ArcFace', desc: 'Face Recognition' },
              { name: 'DeepSORT', desc: 'Face Tracking' },
              { name: 'SilentFace', desc: 'Anti-Spoofing' },
              { name: 'FAISS', desc: 'Vector Search' },
              { name: 'FastAPI', desc: 'Backend API' },
              { name: 'Supabase', desc: 'Database & Auth' },
              { name: 'Next.js', desc: 'Frontend' },
            ].map((tech, i) => (
              <div key={i} className="glass-card p-4 text-center">
                <div className="font-semibold mb-1">{tech.name}</div>
                <div className="text-xs text-white/40">{tech.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center">
              <Eye className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold">AttendX</span>
          </div>
          <p className="text-white/30 text-sm">
            © 2026 AttendX — AAST College of Computing and IT, Smart Village. Graduation Project.
          </p>
        </div>
      </footer>
    </div>
  )
}
