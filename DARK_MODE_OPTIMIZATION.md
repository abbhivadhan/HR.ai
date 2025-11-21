# Dark Mode Optimization Summary

## Pages Updated for Dark Mode Support

This document tracks the dark mode optimization across the application.

### ✅ Already Optimized
- Navigation (has dark mode support)
- Dashboard pages (CandidateDashboard, CompanyDashboard, AdminDashboard)
- Login/Register pages
- Homepage

### 🔄 Need Optimization
1. Contact Page - `/contact`
2. About Page - `/about`
3. Pricing Page - `/pricing`
4. Features Page - `/features`
5. Job Application Page - `/jobs/[id]/apply`
6. Profile Edit Page - `/profile/edit`
7. Jobs Page - `/jobs`
8. Assessments Page - `/assessments`

### Dark Mode Class Pattern

Replace hardcoded light mode classes with dark mode variants:

```tsx
// Background colors
bg-gray-50 → bg-gray-50 dark:bg-gray-900
bg-white → bg-white dark:bg-gray-800

// Text colors
text-gray-900 → text-gray-900 dark:text-white
text-gray-600 → text-gray-600 dark:text-gray-300
text-gray-700 → text-gray-700 dark:text-gray-200

// Borders
border-gray-200 → border-gray-200 dark:border-gray-700
border-gray-300 → border-gray-300 dark:border-gray-600

// Shadows (optional - can be lighter in dark mode)
shadow-lg → shadow-lg dark:shadow-gray-900/50
```

### Implementation Priority
1. High: Contact, About, Pricing (public-facing)
2. Medium: Job Application, Profile Edit
3. Low: Other internal pages

## Status: In Progress
