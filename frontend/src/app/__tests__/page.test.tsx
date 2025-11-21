import { render, screen } from '@testing-library/react'
import Home from '../page'

// Mock framer-motion to avoid issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />)
    
    const heading = screen.getByRole('heading', {
      name: /ai-hr platform/i,
    })
    
    expect(heading).toBeInTheDocument()
  })

  it('renders the description text', () => {
    render(<Home />)
    
    const description = screen.getByText(/revolutionizing recruitment with artificial intelligence/i)
    
    expect(description).toBeInTheDocument()
  })

  it('renders the action buttons', () => {
    render(<Home />)
    
    const getStartedButton = screen.getByRole('button', { name: /get started/i })
    const learnMoreButton = screen.getByRole('button', { name: /learn more/i })
    
    expect(getStartedButton).toBeInTheDocument()
    expect(learnMoreButton).toBeInTheDocument()
  })
})