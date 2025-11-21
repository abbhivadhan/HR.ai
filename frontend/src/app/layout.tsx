import type { Metadata, Viewport } from 'next'
import './globals.css'
import '../styles/accessibility.css'
import { ThemeProvider } from '@/contexts/ThemeContext'
// AuthContext automatically uses Simple Server or Supabase based on env vars
import { AuthProvider } from '@/contexts/AuthContext'
import PerformanceMonitor from '@/components/ui/PerformanceMonitor'
import Navigation from '@/components/layout/Navigation'

export const metadata: Metadata = {
  title: 'HR.ai - AI-Powered Recruitment Platform',
  description: 'Transform your hiring process with HR.ai - the intelligent recruitment platform that connects top talent with great opportunities',
  manifest: '/manifest.json',
  icons: {
    icon: '/icons/icon-192x192.svg',
    apple: '/icons/icon-192x192.svg',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#3b82f6',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#3b82f6" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="HR.ai" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.svg" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const theme = localStorage.getItem('theme') || 'system';
                  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
                  if (isDark) {
                    document.documentElement.classList.add('dark');
                  } else {
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen bg-gray-50 dark:bg-gray-900 keyboard-nav transition-colors">
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <ThemeProvider>
          <AuthProvider>
            <Navigation />
            <div id="main-content" className="pt-16">
              {children}
            </div>
            <PerformanceMonitor />
          </AuthProvider>
        </ThemeProvider>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js');
                });
              }
            `,
          }}
        />
      </body>
    </html>
  )
}