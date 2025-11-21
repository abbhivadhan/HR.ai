'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import CandidateDashboard from '@/components/dashboards/CandidateDashboard'
import CompanyDashboard from '@/components/dashboards/CompanyDashboard'
import AdminDashboard from '@/components/dashboards/AdminDashboard'

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return null
  }

  // Render appropriate dashboard based on user type
  switch (user.userType) {
    case 'CANDIDATE':
      return <CandidateDashboard candidateId={user.id} />
    case 'COMPANY':
      return <CompanyDashboard companyId={user.id} />
    case 'ADMIN':
      return <AdminDashboard adminId={user.id} />
    default:
      return <CandidateDashboard candidateId={user.id} />
  }
}