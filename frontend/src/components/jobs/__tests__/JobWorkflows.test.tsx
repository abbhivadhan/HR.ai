import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { JobPosting, JobSearch, ApplicationTracker, CandidateProfile, JobListing } from '../index'
import { jobService } from '@/services/jobService'
import { JobType, RemoteType, ApplicationStatus } from '@/types/job'

// Mock the job service
jest.mock('@/services/jobService')
const mockJobService = jobService as jest.Mocked<typeof jobService>

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => children,
}))

// Mock react-select
jest.mock('react-select', () => {
  return ({ options, onChange, value, isMulti, placeholder }: any) => (
    <select
      data-testid="react-select"
      onChange={(e) => {
        const selectedValue = e.target.value
        if (isMulti) {
          onChange([{ value: selectedValue, label: selectedValue }])
        } else {
          onChange({ value: selectedValue, label: selectedValue })
        }
      }}
      value={isMulti ? value?.map((v: any) => v.value) : value?.value}
      multiple={isMulti}
    >
      <option value="">{placeholder}</option>
      {options?.map((option: any) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  )
})

// Mock TipTap editor
jest.mock('@tiptap/react', () => ({
  useEditor: () => ({
    getHTML: () => '<p>Test content</p>',
    isActive: () => false,
    chain: () => ({
      focus: () => ({
        toggleBold: () => ({ run: jest.fn() }),
        toggleItalic: () => ({ run: jest.fn() }),
        toggleCode: () => ({ run: jest.fn() }),
        toggleBulletList: () => ({ run: jest.fn() }),
        toggleOrderedList: () => ({ run: jest.fn() }),
        toggleHeading: () => ({ run: jest.fn() }),
      }),
    }),
  }),
  EditorContent: ({ editor }: any) => <div data-testid="editor-content">Editor</div>,
}))

const mockJob = {
  id: '1',
  company_id: 'company-1',
  title: 'Senior Software Engineer',
  description: '<p>Great opportunity for a senior developer</p>',
  summary: 'Join our amazing team',
  job_type: JobType.FULL_TIME,
  experience_level: 'senior',
  department: 'Engineering',
  location: 'San Francisco, CA',
  remote_type: RemoteType.HYBRID,
  salary_min: 120000,
  salary_max: 180000,
  salary_currency: 'USD',
  benefits: ['Health Insurance', '401k'],
  requirements: '<p>5+ years experience</p>',
  responsibilities: '<p>Lead development projects</p>',
  qualifications: '<p>Computer Science degree preferred</p>',
  status: 'active' as any,
  is_featured: false,
  is_urgent: false,
  tags: ['javascript', 'react', 'node.js'],
  posted_at: '2023-10-01T00:00:00Z',
  created_at: '2023-10-01T00:00:00Z',
  updated_at: '2023-10-01T00:00:00Z',
  view_count: 100,
  application_count: 25,
  company: {
    id: 'company-1',
    company_name: 'Tech Corp',
    industry: 'Technology',
    company_size: '100-500',
    website: 'https://techcorp.com',
    description: 'Leading tech company',
    logo_url: 'https://example.com/logo.png',
    verified: true,
  },
  required_skills: [
    { id: '1', name: 'JavaScript', category: 'Programming', level: 'Advanced' },
    { id: '2', name: 'React', category: 'Frontend', level: 'Advanced' },
  ],
}

const mockApplication = {
  id: 'app-1',
  job_posting_id: '1',
  candidate_id: 'candidate-1',
  status: ApplicationStatus.PENDING,
  cover_letter: 'I am very interested in this position',
  ai_match_score: 85,
  applied_at: '2023-10-02T00:00:00Z',
  status_updated_at: '2023-10-02T00:00:00Z',
  created_at: '2023-10-02T00:00:00Z',
  updated_at: '2023-10-02T00:00:00Z',
  job_posting: mockJob,
}

const mockCandidate = {
  id: 'candidate-1',
  user_id: 'user-1',
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  experience_years: 8,
  preferred_locations: ['San Francisco', 'Remote'],
  skills: [
    { id: '1', name: 'JavaScript', category: 'Programming', level: 'Expert' },
    { id: '2', name: 'React', category: 'Frontend', level: 'Advanced' },
  ],
  education: [
    {
      id: '1',
      institution: 'Stanford University',
      degree: 'Bachelor of Science',
      field_of_study: 'Computer Science',
      start_date: '2010-09-01',
      end_date: '2014-06-01',
      grade: '3.8 GPA',
    },
  ],
  certifications: [
    {
      id: '1',
      name: 'AWS Certified Solutions Architect',
      issuing_organization: 'Amazon Web Services',
      issue_date: '2022-01-01',
      expiration_date: '2025-01-01',
    },
  ],
  bio: 'Experienced software engineer with a passion for building scalable applications.',
}

describe('Job Management Workflows', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('JobPosting Component', () => {
    it('renders job posting form correctly', () => {
      render(<JobPosting onSuccess={jest.fn()} onCancel={jest.fn()} />)
      
      expect(screen.getByText('Create New Job Posting')).toBeInTheDocument()
      expect(screen.getByLabelText(/job title/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/job summary/i)).toBeInTheDocument()
    })

    it('handles form submission for new job', async () => {
      mockJobService.createJob.mockResolvedValue(mockJob)
      const onSuccess = jest.fn()
      
      render(<JobPosting onSuccess={onSuccess} onCancel={jest.fn()} />)
      
      // Fill in required fields
      fireEvent.change(screen.getByLabelText(/job title/i), {
        target: { value: 'Test Job' }
      })
      
      // Navigate through steps and submit
      fireEvent.click(screen.getByText('Next'))
      fireEvent.click(screen.getByText('Next'))
      fireEvent.click(screen.getByText('Next'))
      
      const submitButton = screen.getByText('Create Job')
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(mockJobService.createJob).toHaveBeenCalled()
        expect(onSuccess).toHaveBeenCalledWith(mockJob)
      })
    })

    it('handles form submission for editing job', async () => {
      mockJobService.updateJob.mockResolvedValue(mockJob)
      const onSuccess = jest.fn()
      
      render(<JobPosting job={mockJob} onSuccess={onSuccess} onCancel={jest.fn()} />)
      
      expect(screen.getByText('Edit Job Posting')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Senior Software Engineer')).toBeInTheDocument()
    })
  })

  describe('JobSearch Component', () => {
    const mockSearchResponse = {
      jobs: [mockJob],
      total: 1,
      page: 1,
      per_page: 20,
      total_pages: 1,
      filters_applied: {},
    }

    it('renders search interface correctly', () => {
      mockJobService.searchJobs.mockResolvedValue(mockSearchResponse)
      
      render(<JobSearch />)
      
      expect(screen.getByPlaceholderText(/search jobs/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/location/i)).toBeInTheDocument()
      expect(screen.getByText('Filters')).toBeInTheDocument()
    })

    it('performs job search with filters', async () => {
      mockJobService.searchJobs.mockResolvedValue(mockSearchResponse)
      
      render(<JobSearch />)
      
      // Enter search query
      const searchInput = screen.getByPlaceholderText(/search jobs/i)
      fireEvent.change(searchInput, { target: { value: 'software engineer' } })
      
      // Click search button
      fireEvent.click(screen.getByText('Search'))
      
      await waitFor(() => {
        expect(mockJobService.searchJobs).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'software engineer'
          }),
          1,
          20
        )
      })
    })

    it('displays search results correctly', async () => {
      mockJobService.searchJobs.mockResolvedValue(mockSearchResponse)
      
      render(<JobSearch />)
      
      await waitFor(() => {
        expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
        expect(screen.getByText('Tech Corp')).toBeInTheDocument()
        expect(screen.getByText('1 jobs found')).toBeInTheDocument()
      })
    })

    it('handles job selection', async () => {
      mockJobService.searchJobs.mockResolvedValue(mockSearchResponse)
      const onJobSelect = jest.fn()
      
      render(<JobSearch onJobSelect={onJobSelect} />)
      
      await waitFor(() => {
        const jobCard = screen.getByText('Senior Software Engineer').closest('.card')
        fireEvent.click(jobCard!)
        expect(onJobSelect).toHaveBeenCalledWith(mockJob)
      })
    })
  })

  describe('ApplicationTracker Component', () => {
    it('renders application list correctly', async () => {
      mockJobService.getCandidateApplications.mockResolvedValue([mockApplication])
      
      render(<ApplicationTracker />)
      
      await waitFor(() => {
        expect(screen.getByText('My Applications')).toBeInTheDocument()
        expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
        expect(screen.getByText('Pending Review')).toBeInTheDocument()
      })
    })

    it('filters applications by status', async () => {
      mockJobService.getCandidateApplications.mockResolvedValue([mockApplication])
      
      render(<ApplicationTracker />)
      
      await waitFor(() => {
        const filterSelect = screen.getByDisplayValue('All Applications')
        fireEvent.change(filterSelect, { target: { value: ApplicationStatus.PENDING } })
        
        expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
      })
    })

    it('shows application details when selected', async () => {
      mockJobService.getCandidateApplications.mockResolvedValue([mockApplication])
      
      render(<ApplicationTracker />)
      
      await waitFor(() => {
        const applicationCard = screen.getByText('Senior Software Engineer').closest('.card')
        fireEvent.click(applicationCard!)
        
        expect(screen.getByText('Application Details')).toBeInTheDocument()
        expect(screen.getByText('I am very interested in this position')).toBeInTheDocument()
      })
    })
  })

  describe('CandidateProfile Component', () => {
    it('renders candidate profile correctly', async () => {
      mockJobService.getCandidateProfile.mockResolvedValue(mockCandidate)
      
      render(<CandidateProfile candidateId="candidate-1" showContactInfo={true} />)
      
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
        expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
        expect(screen.getByText('8 years experience')).toBeInTheDocument()
      })
    })

    it('switches between tabs correctly', async () => {
      mockJobService.getCandidateProfile.mockResolvedValue(mockCandidate)
      
      render(<CandidateProfile candidateId="candidate-1" />)
      
      await waitFor(() => {
        // Click on Skills tab
        fireEvent.click(screen.getByText('Skills'))
        expect(screen.getByText('Skills & Expertise')).toBeInTheDocument()
        
        // Click on Education tab
        fireEvent.click(screen.getByText('Education'))
        expect(screen.getByText('Education & Certifications')).toBeInTheDocument()
        expect(screen.getByText('Stanford University')).toBeInTheDocument()
      })
    })

    it('shows contact actions when enabled', async () => {
      mockJobService.getCandidateProfile.mockResolvedValue(mockCandidate)
      const onContact = jest.fn()
      
      render(
        <CandidateProfile 
          candidateId="candidate-1" 
          showActions={true}
          onContact={onContact}
        />
      )
      
      await waitFor(() => {
        const contactButton = screen.getByText('Contact')
        fireEvent.click(contactButton)
        expect(onContact).toHaveBeenCalledWith(mockCandidate)
      })
    })
  })

  describe('JobListing Component', () => {
    it('renders job listing in compact mode', () => {
      render(<JobListing job={mockJob} compact={true} />)
      
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
      expect(screen.getByText('Tech Corp')).toBeInTheDocument()
      expect(screen.getByText('full time')).toBeInTheDocument()
    })

    it('renders full job listing with all details', () => {
      render(<JobListing job={mockJob} />)
      
      expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
      expect(screen.getByText('Job Description')).toBeInTheDocument()
      expect(screen.getByText('Requirements')).toBeInTheDocument()
      expect(screen.getByText('About Tech Corp')).toBeInTheDocument()
    })

    it('handles job application', async () => {
      const onApply = jest.fn()
      
      render(<JobListing job={mockJob} onApply={onApply} />)
      
      const applyButton = screen.getByText('Apply Now')
      fireEvent.click(applyButton)
      
      expect(onApply).toHaveBeenCalledWith(mockJob)
    })

    it('handles job saving', async () => {
      mockJobService.saveJob.mockResolvedValue()
      
      render(<JobListing job={mockJob} />)
      
      const saveButton = screen.getByLabelText(/save job/i)
      fireEvent.click(saveButton)
      
      await waitFor(() => {
        expect(mockJobService.saveJob).toHaveBeenCalledWith(mockJob.id)
      })
    })
  })

  describe('Integration Workflows', () => {
    it('completes full job posting workflow', async () => {
      mockJobService.createJob.mockResolvedValue(mockJob)
      const onSuccess = jest.fn()
      
      render(<JobPosting onSuccess={onSuccess} onCancel={jest.fn()} />)
      
      // Step 1: Basic Info
      fireEvent.change(screen.getByLabelText(/job title/i), {
        target: { value: 'Test Job' }
      })
      fireEvent.click(screen.getByText('Next'))
      
      // Step 2: Details (skip for brevity)
      fireEvent.click(screen.getByText('Next'))
      
      // Step 3: Requirements (skip for brevity)
      fireEvent.click(screen.getByText('Next'))
      
      // Step 4: Submit
      fireEvent.click(screen.getByText('Create Job'))
      
      await waitFor(() => {
        expect(mockJobService.createJob).toHaveBeenCalled()
        expect(onSuccess).toHaveBeenCalled()
      })
    })

    it('completes job search to application workflow', async () => {
      const mockSearchResponse = {
        jobs: [mockJob],
        total: 1,
        page: 1,
        per_page: 20,
        total_pages: 1,
        filters_applied: {},
      }
      
      mockJobService.searchJobs.mockResolvedValue(mockSearchResponse)
      mockJobService.saveJob.mockResolvedValue()
      
      const onJobSelect = jest.fn()
      
      render(<JobSearch onJobSelect={onJobSelect} />)
      
      // Wait for initial search
      await waitFor(() => {
        expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument()
      })
      
      // Save job
      const saveButton = screen.getByLabelText(/save job/i)
      fireEvent.click(saveButton)
      await waitFor(() => {
        expect(mockJobService.saveJob).toHaveBeenCalled()
      })
      
      // Select job
      const jobCard = screen.getByText('Senior Software Engineer').closest('.card')
      fireEvent.click(jobCard!)
      
      expect(onJobSelect).toHaveBeenCalledWith(mockJob)
    })
  })
})