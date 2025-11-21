# Quick Test Guide - Candidate Dashboard

## How to Test All Buttons

### Prerequisites
1. Start the development server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Login as a candidate user:
   - Go to `http://localhost:3000/auth/login`
   - Use candidate credentials

3. Navigate to dashboard:
   - Go to `http://localhost:3000/dashboard`

## Button Testing Checklist

### ✅ Main Dashboard Area

#### AI Video Interview Card
- [ ] Click **"Start AI Interview"**
  - Expected: Navigate to `/interviews/ai-video/demo-{timestamp}`
  - Should see: AI interview interface with avatar

#### Recommended Jobs Section
- [ ] Click **"Apply Now"** on any job card
  - Expected: Navigate to `/jobs/{id}/apply`
  - Should see: Job application form

- [ ] Click **"View All"** button
  - Expected: Navigate to `/jobs`
  - Should see: Complete job listings page

#### Profile Strength Card
- [ ] Click **"Add Video Introduction"**
  - Expected: Navigate to `/portfolio`
  - Should see: Video portfolio page with recorder

- [ ] Click **"Add More Skills"**
  - Expected: Navigate to `/profile/edit`
  - Should see: Profile editor with skills section

- [ ] Click **"Optimize Resume"**
  - Expected: Navigate to `/resume`
  - Should see: Resume builder interface

- [ ] Click **"Complete Profile Now"**
  - Expected: Navigate to `/profile/edit`
  - Should see: Profile editor page

- [ ] Click **"View Details"**
  - Expected: Open profile details modal
  - Should see: Detailed profile breakdown modal

#### Profile Details Modal (after clicking "View Details")
- [ ] Click **"Add Skills →"**
  - Expected: Navigate to `/profile/edit#skills`
  - Should see: Profile editor with skills section focused

- [ ] Click **"Record Video →"**
  - Expected: Navigate to `/portfolio`
  - Should see: Video portfolio page

- [ ] Click **"Complete Profile"**
  - Expected: Navigate to `/profile/edit`
  - Should see: Profile editor page

- [ ] Click **"Close"**
  - Expected: Close modal
  - Should see: Return to dashboard

### ✅ Right Sidebar

#### External Assessments Card
- [ ] Click **"Browse Tests"**
  - Expected: Navigate to `/assessments/external`
  - Should see: External assessment providers page

#### AI-Powered Tools Section
- [ ] Click **"Career Coach"**
  - Expected: Navigate to `/career-coach`
  - Should see: AI career coach chat interface

- [ ] Click **"Resume Builder"**
  - Expected: Navigate to `/resume`
  - Should see: Resume builder with templates

- [ ] Click **"Smart Scheduling"**
  - Expected: Navigate to `/scheduling`
  - Should see: Smart calendar interface

- [ ] Click **"Video Portfolio"**
  - Expected: Navigate to `/portfolio`
  - Should see: Portfolio management page

- [ ] Click **"Skill Assessments"**
  - Expected: Navigate to `/assessments`
  - Should see: Assessment list page

- [ ] Click **"Job Matching"**
  - Expected: Navigate to `/jobs/search`
  - Should see: Job search with filters

#### Quick Actions Section
- [ ] Click **"Take Assessment"**
  - Expected: Navigate to `/assessments`
  - Should see: Available assessments list

- [ ] Click **"Update Profile"**
  - Expected: Navigate to `/profile/edit`
  - Should see: Profile editor

- [ ] Click **"Browse Jobs"**
  - Expected: Navigate to `/jobs/search`
  - Should see: Job search page

### ✅ Notifications

#### Notification Center (Bell Icon)
- [ ] Click notification bell icon
  - Expected: Open notifications dropdown
  - Should see: List of notifications

- [ ] Click **"Assessment Completed"** notification
  - Expected: Navigate to `/assessments/results/{id}`
  - Should see: Detailed assessment results

- [ ] Click **"New Job Match"** notification
  - Expected: Navigate to `/jobs/recommendations`
  - Should see: Personalized job recommendations

- [ ] Click **"Profile Incomplete"** notification
  - Expected: Navigate to `/profile/edit`
  - Should see: Profile editor

## Page-Specific Testing

### Assessment Results Page (`/assessments/results/{id}`)
Test by clicking on an assessment notification or completing an assessment.

**What to verify:**
- [ ] Score is displayed prominently
- [ ] Stats show correct/incorrect/time
- [ ] Question review shows all questions
- [ ] Explanations are visible
- [ ] "Take Another Assessment" button works
- [ ] "Back to Assessments" button works

### Job Recommendations Page (`/jobs/recommendations`)
Test by clicking "New Job Match" notification.

**What to verify:**
- [ ] Job cards display with match scores
- [ ] Filter buttons work (All, High, Medium)
- [ ] Save/bookmark button toggles
- [ ] "View Details" navigates to job page
- [ ] "Apply Now" navigates to application form
- [ ] Match score colors are correct (green 90%+, blue 80-89%, yellow 70-79%)

### Candidate Detail Page (`/dashboard/candidates/{id}`)
Test by clicking on a candidate card (company dashboard).

**What to verify:**
- [ ] Profile information displays correctly
- [ ] Contact details are visible
- [ ] Skills are shown as tags
- [ ] Assessment scores show progress bars
- [ ] Application history is listed
- [ ] "Message Candidate" button is present
- [ ] "Schedule Interview" button is present
- [ ] "View Resume" button is present (if resume exists)
- [ ] "Back to Candidates" button works

### Profile Page (`/profile`)
Test by clicking any "Update Profile" button.

**What to verify:**
- [ ] Redirects to `/profile/edit`
- [ ] No errors in console
- [ ] Smooth transition

## Responsive Testing

### Mobile View (< 768px)
1. Open Chrome DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select "iPhone 12 Pro" or similar
4. Test all buttons:
   - [ ] Buttons are touch-friendly (min 44px)
   - [ ] Text is readable
   - [ ] No horizontal scroll
   - [ ] Modals fit screen
   - [ ] Navigation works

### Tablet View (768px - 1024px)
1. Select "iPad" in DevTools
2. Test all buttons:
   - [ ] Layout adjusts properly
   - [ ] Two-column layout works
   - [ ] All content visible
   - [ ] Touch targets adequate

### Desktop View (> 1024px)
1. Use full browser window
2. Test all buttons:
   - [ ] Three-column layout works
   - [ ] Hover effects work
   - [ ] Animations smooth
   - [ ] All features accessible

## Dark Mode Testing

1. Toggle dark mode (if theme switcher available)
2. Verify all pages:
   - [ ] Dashboard looks good in dark mode
   - [ ] Assessment results readable
   - [ ] Job recommendations clear
   - [ ] Candidate details visible
   - [ ] No contrast issues
   - [ ] Colors are appropriate

## Browser Testing

Test in multiple browsers:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if on Mac)

## Performance Testing

1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run audit on dashboard
4. Verify scores:
   - [ ] Performance > 80
   - [ ] Accessibility > 90
   - [ ] Best Practices > 90
   - [ ] SEO > 80

## Error Handling Testing

### Test Authentication
- [ ] Logout and try to access dashboard
  - Expected: Redirect to login page

- [ ] Access protected pages without login
  - Expected: Redirect to login page

### Test Invalid Routes
- [ ] Navigate to `/assessments/results/invalid-id`
  - Expected: Show "Results not found" message

- [ ] Navigate to `/dashboard/candidates/invalid-id`
  - Expected: Show "Candidate not found" message

### Test Network Errors
1. Open DevTools Network tab
2. Set throttling to "Offline"
3. Try to load dashboard
   - Expected: Show loading state or error message

## Console Error Check

Throughout testing, keep DevTools console open:
- [ ] No red errors
- [ ] No yellow warnings (or only expected ones)
- [ ] No 404 errors for resources
- [ ] No TypeScript errors

## Quick Smoke Test (5 minutes)

If you're short on time, test these critical paths:

1. **Job Application Flow** (1 min)
   - Dashboard → Apply Now → Application Form

2. **Assessment Flow** (1 min)
   - Dashboard → Take Assessment → Assessment List

3. **Profile Update Flow** (1 min)
   - Dashboard → Update Profile → Profile Editor

4. **AI Tools Flow** (1 min)
   - Dashboard → Career Coach → AI Interface

5. **Job Discovery Flow** (1 min)
   - Dashboard → Browse Jobs → Job Search

## Automated Testing (Optional)

If you want to run automated tests:

```bash
cd frontend
npm run test
```

This will run:
- Unit tests for components
- Integration tests for pages
- Accessibility tests

## Bug Reporting Template

If you find any issues, report them using this template:

```
**Bug Title**: [Brief description]

**Steps to Reproduce**:
1. Go to dashboard
2. Click [button name]
3. See error

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Browser**: Chrome 120
**Device**: Desktop
**Screenshot**: [Attach if possible]
**Console Errors**: [Copy any errors]
```

## Success Criteria

All tests pass when:
- ✅ All buttons navigate to correct pages
- ✅ No console errors
- ✅ Pages load within 2 seconds
- ✅ Responsive on all devices
- ✅ Dark mode works correctly
- ✅ Animations are smooth
- ✅ No broken links
- ✅ Authentication works
- ✅ Error handling works
- ✅ Accessibility score > 90

## Summary

**Total Buttons to Test**: 20+
**Estimated Testing Time**: 15-20 minutes (full test)
**Quick Test Time**: 5 minutes (smoke test)

**Status**: Ready for testing! 🚀

All candidate dashboard buttons are implemented and ready for user testing.
