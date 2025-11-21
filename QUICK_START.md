# 🚀 Quick Start Guide - AI HR Platform

## Prerequisites
- Node.js 18+ 
- Python 3.9+
- PostgreSQL 13+
- Redis (optional, for caching)

## 1. Install Dependencies

### Frontend
```bash
cd frontend
npm install
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Setup Database

```bash
# Create database
createdb ai_hr_platform

# Run migrations
cd backend
alembic upgrade head
```

## 3. Configure Environment

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:password@localhost/ai_hr_platform
SECRET_KEY=your-super-secret-key-change-this-in-production
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000
```

## 4. Run the Application

### Terminal 1 - Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 6. Test Accounts

### Candidate Account
- Email: candidate@example.com
- Password: password123

### Company Account
- Email: company@example.com
- Password: password123

### Admin Account
- Email: admin@example.com
- Password: admin123

## 7. Key Features to Test

### As a Candidate:
1. ✅ Register/Login
2. ✅ Complete profile
3. ✅ Browse jobs
4. ✅ Apply to jobs
5. ✅ Take assessments
6. ✅ Schedule interviews
7. ✅ View dashboard analytics

### As a Company:
1. ✅ Register/Login
2. ✅ Post a job
3. ✅ Review applications
4. ✅ Browse candidates
5. ✅ Schedule interviews
6. ✅ View analytics
7. ✅ Manage team

### As an Admin:
1. ✅ Login
2. ✅ View platform metrics
3. ✅ Manage users
4. ✅ View analytics
5. ✅ System settings

## 8. Common Issues & Solutions

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Restart PostgreSQL
brew services restart postgresql  # macOS
sudo service postgresql restart   # Linux
```

### Module Not Found
```bash
# Frontend
cd frontend && npm install

# Backend
cd backend && pip install -r requirements.txt
```

### CORS Errors
- Ensure CORS_ORIGINS in backend .env includes http://localhost:3000
- Clear browser cache
- Try incognito mode

## 9. Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- Frontend: Changes auto-refresh
- Backend: API restarts on file changes

### Debug Mode
```bash
# Frontend with debug
npm run dev -- --debug

# Backend with debug
uvicorn app.main:app --reload --log-level debug
```

### Database Reset
```bash
cd backend
alembic downgrade base
alembic upgrade head
```

### Clear Cache
```bash
# Frontend
rm -rf frontend/.next
rm -rf frontend/node_modules/.cache

# Backend
find . -type d -name __pycache__ -exec rm -r {} +
```

## 10. Testing

### Frontend Tests
```bash
cd frontend
npm test
npm run test:watch  # Watch mode
```

### Backend Tests
```bash
cd backend
pytest
pytest --cov  # With coverage
pytest -v     # Verbose
```

### E2E Tests
```bash
cd tests
pytest e2e/
```

## 11. Build for Production

### Frontend
```bash
cd frontend
npm run build
npm start
```

### Backend
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 12. Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 13. Useful Commands

```bash
# Check all services
npm run check-all

# Format code
npm run format

# Lint code
npm run lint

# Generate API client
npm run generate-api

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 14. Next Steps

1. ✅ Explore the dashboard
2. ✅ Test all features
3. ✅ Review API documentation
4. ✅ Customize branding
5. ✅ Configure email service
6. ✅ Set up monitoring
7. ✅ Deploy to staging
8. ✅ Run security audit
9. ✅ Performance testing
10. ✅ Go live! 🎉

## 15. Support & Resources

- **Documentation**: Check `/docs` in the app
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs
- **Community**: Join discussions

## 🎉 You're All Set!

The AI HR Platform is now running locally. Start exploring and building amazing recruitment experiences!

---

**Need Help?** Check `IMPLEMENTATION_COMPLETE.md` for detailed feature documentation.
