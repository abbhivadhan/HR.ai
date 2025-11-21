# Pre-Deployment Checklist

## ✅ Before You Deploy

### 1. Supabase Setup
- [ ] Created Supabase account
- [ ] Created new project
- [ ] Saved database password securely
- [ ] Ran database migration (001_initial_schema.sql)
- [ ] Verified all tables created
- [ ] Enabled RLS on all tables
- [ ] Configured authentication providers
- [ ] Copied API keys (URL and anon key)

### 2. Environment Configuration
- [ ] Created frontend/.env.local
- [ ] Added NEXT_PUBLIC_SUPABASE_URL
- [ ] Added NEXT_PUBLIC_SUPABASE_ANON_KEY
- [ ] Added NEXT_PUBLIC_API_URL
- [ ] Verified no sensitive keys in git

### 3. Dependencies
- [ ] Installed @supabase/supabase-js in frontend
- [ ] Ran npm install in frontend directory
- [ ] No dependency vulnerabilities (npm audit)
- [ ] All packages up to date

### 4. Code Quality
- [ ] No TypeScript errors (npm run type-check)
- [ ] No linting errors (npm run lint)
- [ ] Build succeeds locally (npm run build)
- [ ] Tested locally (npm run dev)

### 5. Testing
- [ ] User registration works
- [ ] User login works
- [ ] User logout works
- [ ] Password reset works
- [ ] Job creation works
- [ ] Job application works
- [ ] Assessment submission works
- [ ] Interview scheduling works

### 6. Security
- [ ] RLS policies tested
- [ ] No hardcoded secrets
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Input validation implemented
- [ ] Authentication required for protected routes

### 7. Vercel Setup
- [ ] Installed Vercel CLI
- [ ] Logged into Vercel account
- [ ] Created new project (or linked existing)
- [ ] Added environment variables in Vercel
- [ ] Configured custom domain (if applicable)

### 8. Documentation
- [ ] Read DEPLOYMENT_SUPABASE.md
- [ ] Read SUPABASE_INTEGRATION_GUIDE.md
- [ ] Understand database schema
- [ ] Know how to access logs
- [ ] Know how to rollback if needed

## 🚀 Deployment Steps

### Step 1: Final Build Test
```bash
cd frontend
npm run build
```

### Step 2: Deploy to Vercel
```bash
vercel --prod
```

### Step 3: Add Environment Variables
In Vercel Dashboard:
1. Go to Settings > Environment Variables
2. Add all NEXT_PUBLIC_* variables
3. Redeploy if needed

### Step 4: Test Production
- [ ] Visit deployed URL
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Test core features
- [ ] Check console for errors
- [ ] Verify data in Supabase

## 📊 Post-Deployment

### Immediate (First Hour)
- [ ] Monitor error logs
- [ ] Check Supabase usage
- [ ] Test all critical paths
- [ ] Verify email delivery (if configured)
- [ ] Check performance metrics

### First Day
- [ ] Monitor user signups
- [ ] Check for any errors
- [ ] Review database queries
- [ ] Verify backups working
- [ ] Test on multiple devices

### First Week
- [ ] Analyze usage patterns
- [ ] Optimize slow queries
- [ ] Review security logs
- [ ] Plan for scaling
- [ ] Gather user feedback

## 🔧 Rollback Plan

If something goes wrong:

### Option 1: Revert Deployment
```bash
# In Vercel Dashboard
1. Go to Deployments
2. Find previous working deployment
3. Click "..." > "Promote to Production"
```

### Option 2: Fix and Redeploy
```bash
# Fix the issue locally
git commit -m "Fix: issue description"
git push
vercel --prod
```

### Option 3: Database Rollback
```bash
# In Supabase Dashboard
1. Go to Database > Backups
2. Restore from previous backup
3. Note: Only available on Pro plan
```

## 📞 Support Contacts

### Technical Issues
- Supabase Support: https://supabase.com/support
- Vercel Support: https://vercel.com/support
- GitHub Issues: [Your repo URL]

### Emergency Contacts
- Database Admin: [Your contact]
- DevOps Lead: [Your contact]
- Project Manager: [Your contact]

## 📝 Notes

### Known Issues
- List any known issues here
- Include workarounds if available

### Future Improvements
- List planned improvements
- Note any technical debt

### Monitoring URLs
- Supabase Dashboard: https://app.supabase.com
- Vercel Dashboard: https://vercel.com/dashboard
- Production URL: [Your URL]
- Staging URL: [Your URL]

## ✨ Final Checks

Before clicking deploy:
- [ ] All checklist items completed
- [ ] Team notified of deployment
- [ ] Backup plan ready
- [ ] Monitoring configured
- [ ] Support contacts available
- [ ] Documentation updated
- [ ] Confidence level: High

## 🎉 Ready to Deploy!

If all items are checked, you're ready to deploy!

Run: `./deploy.sh` or `vercel --prod`

Good luck! 🚀
