import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { AuthProvider } from '@/contexts/AuthContext'
import Home from '@/app/page'

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    h1: ({ children, ...props }: any) => <h1 {...props}>{children}</h1>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
  useScroll: () => ({ scrollYProgress: { get: () => 0 } }),
  useTransform: () => '0%',
  AnimatePresence: ({ children }: any) => children,
}))

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: any) => <a href={href}>{children}</a>
})

const MockProviders = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>
    <AuthProvider>
      {children}
    </AuthProvider>
  </ThemeProvider>
)

describe('Homepage', () => {
  it('renders the main heading', () => {
    render(
      <MockProviders>
        <Home />
      </MockProviders>
    )
    
    expect(screen.getByText(/HR\.ai/)).toBeInTheDocument()
    expect(screen.getByText(/The Future of/)).toBeInTheDocument()
    expect(screen.getByText(/AI-Powered Hiring/)).toBeInTheDocument()
  })

  it('renders feature sections', () => {
    render(
      <MockProviders>
        <Home />
      </MockProviders>
    )
    
    expect(screen.getByText('Built for Everyone')).toBeInTheDocument()
    expect(screen.getByText('How It Works')).toBeInTheDocument()
  })

  it('renders call-to-action buttons', () => {
    render(
      <MockProviders>
        <Home />
      </MockProviders>
    )
    
    expect(screen.getByText('Start Free Trial')).toBeInTheDocument()
    expect(screen.getByText('Explore Features')).toBeInTheDocument()
  })

  it('renders stats section', () => {
    render(
      <MockProviders>
        <Home />
      </MockProviders>
    )
    
    expect(screen.getByText('10K+')).toBeInTheDocument()
    expect(screen.getByText('Active Users')).toBeInTheDocument()
    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('Match Accuracy')).toBeInTheDocument()
  })
})