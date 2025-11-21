# AI-HR Platform

A comprehensive AI-powered recruitment and hiring platform built with modern technologies.

## 🚀 Features

- **AI-Powered Assessments**: Intelligent skill evaluation and testing
- **Video Interviews**: AI-driven video interview analysis
- **Smart Job Matching**: ML-based candidate-job matching
- **Modern UI/UX**: Responsive design with smooth animations
- **Secure Authentication**: Multi-factor authentication and JWT tokens
- **Real-time Analytics**: Comprehensive dashboards and reporting

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **MongoDB** - Unstructured data storage
- **Celery** - Background task processing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library

### AI/ML
- **TensorFlow/Keras** - Deep learning models
- **OpenAI GPT** - Natural language processing
- **scikit-learn** - Machine learning algorithms
- **OpenCV** - Computer vision for video analysis

## 🏗 Project Structure

```
ai-hr-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Next.js frontend
│   ├── src/
│   │   └── app/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml       # Production compose
├── docker-compose.dev.yml   # Development compose
└── .github/workflows/       # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-hr-platform
   ```

2. **Start development environment**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

3. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development (without Docker)

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Production Build
```bash
docker-compose up -d
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- Database connections
- JWT secrets
- External API keys
- Environment settings

## 🔧 Development

### Adding New Features
1. Create feature branch from `develop`
2. Implement changes following the project structure
3. Add tests for new functionality
4. Submit pull request

### Code Quality
- Backend: Follow PEP 8 standards
- Frontend: Use ESLint and Prettier
- Tests: Maintain >90% coverage
- Security: Regular dependency updates

## 📚 API Documentation

Interactive API documentation is available at `/docs` when running the backend server.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository.