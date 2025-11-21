# Supabase Deployment Guide

## Quick Start Deployment

### Step 1: Set Up Supabase Project

1. Go to https://supabase.com and create an account
2. Click "New Project"
3. Fill in project details:
   - Name: ai-hr-platform
   - Database Password: (generate a strong password)
   - Region: Choose closest to your users
4. Wait for project to be created (~2 minutes)

### Step 2: Run Database Migrations

1. In Supabase Dashboard, go to SQL Editor
2. Copy the contents of `supabase/migrations/001_initial_schema.sql`
3. Paste into SQL Editor and click "Run"
4. Verify all tables were created successfully

### Step 3: Configure Authentication

1. Go to Authentication > Providers
2. Enable Email provider
3. Configure email templates (optional)
4. Set up redirect URLs:
   - Site URL: `https://your-domain.com`
   - Redirect URLs: `https://your-domain.com/auth/callback`

### Step 4: Get API Keys

1. Go to Project Settings > API
2. Copy these values:
   - Project URL
   - anon/public key
   - service_role key (keep secret!)

### Step 5: Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Install Supabase client:
```bash
npm install @supabase/supabase-js
```

4. Deploy to Vercel:
```bash
vercel --prod
```

5. Add environment variables in Vercel Dashboard:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL`

### Step 6: Configure Custom Domain (Optional)

1. In Vercel Dashboard, go to your project
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. Update Supabase redirect URLs with new domain

### Step 7: Test Deployment

1. Visit your deployed site
2. Test user registration
3. Test login/logout
4. Test creating a job posting
5. Test applying to a job
6. Verify data appears in Supabase Dashboard

## Environment Variables Reference

### Required for Frontend
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_API_URL=https://xxxxx.supabase.co
```

### Optional
```env
NEXT_PUBLIC_APP_URL=https://your-domain.com
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

## Post-Deployment Checklist

- [ ] Database tables created
- [ ] RLS policies enabled
- [ ] Authentication configured
- [ ] Frontend deployed
- [ ] Environment variables set
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Test core features
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review security settings

## Monitoring and Maintenance

### Database Monitoring
- Check Supabase Dashboard > Database > Usage
- Monitor query performance
- Review slow queries
- Set up alerts for high usage

### Application Monitoring
- Use Vercel Analytics
- Set up error tracking (Sentry)
- Monitor API response times
- Track user engagement

### Backups
- Supabase automatically backs up your database
- Pro plan: Point-in-time recovery
- Export data regularly for extra safety

## Scaling Considerations

### Database
- Supabase Free tier: 500MB database, 2GB bandwidth
- Pro tier: 8GB database, 50GB bandwidth
- Enterprise: Custom limits

### Frontend
- Vercel automatically scales
- Use CDN for static assets
- Implement caching strategies

### Performance Optimization
- Enable database indexes (already in migration)
- Use Supabase Edge Functions for heavy operations
- Implement pagination for large datasets
- Use connection pooling

## Troubleshooting

### Common Issues

**Issue: "Invalid API key"**
- Solution: Verify environment variables are set correctly
- Check for typos in .env files
- Ensure you're using anon key for frontend

**Issue: "Row Level Security policy violation"**
- Solution: Check RLS policies in Supabase Dashboard
- Verify user is authenticated
- Review policy conditions

**Issue: "Database connection failed"**
- Solution: Check Supabase project status
- Verify DATABASE_URL is correct
- Check if project is paused (free tier)

**Issue: "CORS errors"**
- Solution: Add your domain to Supabase allowed origins
- Check API URL configuration
- Verify authentication headers

## Security Best Practices

1. **Never expose service_role key** - Only use on backend
2. **Enable RLS on all tables** - Already done in migration
3. **Validate all inputs** - Implement on frontend and backend
4. **Use HTTPS only** - Enforced by Vercel and Supabase
5. **Implement rate limiting** - Use Supabase built-in limits
6. **Regular security audits** - Review access logs
7. **Keep dependencies updated** - Run `npm audit` regularly

## Cost Estimation

### Supabase Pricing
- Free: $0/month (2 projects, 500MB database)
- Pro: $25/month (unlimited projects, 8GB database)
- Team: $599/month (SOC2, custom limits)

### Vercel Pricing
- Hobby: $0/month (personal projects)
- Pro: $20/month per user (commercial use)
- Enterprise: Custom pricing

### Total Estimated Cost
- Development: $0/month (free tiers)
- Production (small): $45/month (Supabase Pro + Vercel Pro)
- Production (scale): $600+/month (Team plans)

## Support Resources

- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Vercel Docs: https://vercel.com/docs
- GitHub Issues: Create issues in your repo

## Next Steps

1. Complete deployment following this guide
2. Test all features thoroughly
3. Set up monitoring and alerts
4. Configure custom domain
5. Implement analytics
6. Plan for scaling
7. Regular maintenance and updates
