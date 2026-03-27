import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AttendX - AI Attendance System',
  description: 'AI-powered attendance system using facial recognition',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-dark-950 text-white antialiased min-h-screen">
        {children}
      </body>
    </html>
  )
}
