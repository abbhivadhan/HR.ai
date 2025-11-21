# 🎓 External Assessments Integration Guide

## Overview

The AI HR Platform now integrates with leading assessment providers to offer real, industry-standard skill tests. This allows candidates to take professional assessments and companies to evaluate skills using trusted platforms.

---

## 🌐 Integrated Providers

### 1. **HackerRank** 💻
- **Website**: https://www.hackerrank.com/work/tests
- **Specialization**: Coding assessments, algorithms, data structures
- **Test Types**:
  - Programming languages (Python, JavaScript, Java, C++, etc.)
  - Algorithms and data structures
  - Problem-solving
  - SQL and databases
- **Duration**: 30-90 minutes
- **Pricing**: Contact for enterprise pricing

### 2. **CodeSignal** 🔷
- **Website**: https://codesignal.com/developers/
- **Specialization**: General Coding Assessment (GCA), role-specific tests
- **Test Types**:
  - General Coding Assessment
  - Frontend development
  - Backend development
  - Full-stack development
- **Duration**: 60-75 minutes
- **Pricing**: Contact for enterprise pricing

### 3. **TestGorilla** 🦍
- **Website**: https://www.testgorilla.com/
- **Specialization**: Cognitive, personality, and soft skills
- **Test Types**:
  - Cognitive ability
  - Personality (Big 5)
  - Communication skills
  - Critical thinking
  - Culture fit
- **Duration**: 20-40 minutes
- **Pricing**: Starts at $75/month

### 4. **Pluralsight Skills** 📚
- **Website**: https://www.pluralsight.com/product/skills
- **Specialization**: Technology skills assessments
- **Test Types**:
  - Programming languages
  - Cloud platforms (AWS, Azure, GCP)
  - DevOps and infrastructure
  - Data science and ML
- **Duration**: 30-50 minutes
- **Pricing**: Contact for enterprise pricing

---

## 🚀 Setup Instructions

### Step 1: Get API Keys

#### HackerRank
1. Sign up at https://www.hackerrank.com/work
2. Navigate to Settings > API
3. Generate API key
4. Add to `.env`: `HACKERRANK_API_KEY=your_key_here`

#### CodeSignal
1. Sign up at https://codesignal.com/developers/
2. Go to Account > API Access
3. Create API token
4. Add to `.env`: `CODESIGNAL_API_KEY=your_key_here`

#### TestGorilla
1. Sign up at https://www.testgorilla.com/
2. Navigate to Settings > Integrations > API
3. Generate API key
4. Add to `.env`: `TESTGORILLA_API_KEY=your_key_here`

#### Pluralsight
1. Contact Pluralsight for enterprise access
2. Request API credentials
3. Add to `.env`: `PLURALSIGHT_API_KEY=your_key_here`

### Step 2: Configure Environment

Add to `backend/.env`:
```env
# External Assessment Providers
HACKERRANK_API_KEY=your_hackerrank_key
CODESIGNAL_API_KEY=your_codesignal_key
TESTGORILLA_API_KEY=your_testgorilla_key
PLURALSIGHT_API_KEY=your_pluralsight_key
```

### Step 3: Test Integration

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test API endpoint
curl http://localhost:8000/api/assessments/external/tests
```

---

## 📋 Features

### For Candidates

1. **Browse Assessments**
   - View all available tests from multiple providers
   - Filter by provider, skill, or difficulty
   - See test duration and requirements

2. **Take Tests**
   - One-click test initiation
   - Redirected to provider's platform
   - Seamless authentication

3. **Track Progress**
   - View test status
   - See completion dates
   - Access results and scores

4. **Certificates**
   - Earn certificates from providers
   - Display on profile
   - Share with employers

### For Companies

1. **Assign Tests**
   - Recommend tests to candidates
   - Require specific assessments
   - Set deadlines

2. **View Results**
   - Access detailed scores
   - Compare candidates
   - Export reports

3. **Custom Test Libraries**
   - Create test combinations
   - Build assessment workflows
   - Set passing scores

---

## 🔧 API Endpoints

### Get Available Tests
```http
GET /api/assessments/external/tests
GET /api/assessments/external/tests?provider=hackerrank
GET /api/assessments/external/tests?skill=Python
```

### Start Test
```http
POST /api/assessments/external/start
Content-Type: application/json

{
  "provider": "hackerrank",
  "test_id": "hr_python_001"
}
```

### Get Results
```http
GET /api/assessments/external/results/{session_id}?provider=hackerrank
```

### Get Recommendations
```http
GET /api/assessments/external/recommended?job_id=123
```

---

## 💡 Usage Examples

### Frontend Integration

```typescript
// Browse external assessments
import { useRouter } from 'next/navigation'

const router = useRouter()

// Navigate to external assessments
router.push('/assessments/external')

// Start a specific test
const startTest = async (test) => {
  const response = await fetch('/api/assessments/external/start', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      provider: test.provider,
      test_id: test.id
    })
  })
  
  const data = await response.json()
  window.open(data.test_url, '_blank')
}
```

### Backend Integration

```python
from app.services.external_assessment_service import external_assessment_service

# Get all tests
tests = await external_assessment_service.get_all_available_tests()

# Get tests by skill
python_tests = await external_assessment_service.get_tests_by_skill("Python")

# Create test session
session = await external_assessment_service.create_test_session(
    provider_name="hackerrank",
    test_id="hr_python_001",
    candidate_email="candidate@example.com"
)

# Get results
results = await external_assessment_service.get_test_results(
    provider_name="hackerrank",
    session_id=session["session_id"]
)
```

---

## 🎯 Best Practices

### For Candidates

1. **Prepare Before Testing**
   - Review test requirements
   - Check technical setup
   - Ensure stable internet

2. **During the Test**
   - Read instructions carefully
   - Manage time effectively
   - Don't refresh the page

3. **After the Test**
   - Review results
   - Identify improvement areas
   - Retake if needed

### For Companies

1. **Test Selection**
   - Choose relevant tests
   - Match difficulty to role
   - Consider test duration

2. **Candidate Communication**
   - Explain test purpose
   - Provide preparation resources
   - Set clear expectations

3. **Results Evaluation**
   - Consider context
   - Don't rely solely on scores
   - Combine with other assessments

---

## 🔒 Security & Privacy

### Data Protection
- All API keys encrypted
- Secure token exchange
- No sensitive data stored

### Candidate Privacy
- Results only shared with authorized users
- Candidates control data sharing
- GDPR compliant

### Compliance
- SOC 2 Type II certified providers
- GDPR and CCPA compliant
- Regular security audits

---

## 📊 Pricing

### Development Mode
- **Free**: Mock tests for development
- **No API keys required**: Use mock data
- **Full functionality**: Test all features

### Production Mode
- **HackerRank**: Contact for pricing
- **CodeSignal**: Contact for pricing
- **TestGorilla**: From $75/month
- **Pluralsight**: Contact for pricing

### Cost Optimization
- Use test credits wisely
- Batch candidate invitations
- Monitor usage analytics

---

## 🐛 Troubleshooting

### Common Issues

**API Key Not Working**
```bash
# Check environment variables
echo $HACKERRANK_API_KEY

# Verify key format
# Should be: hrc_xxxxxxxxxxxxx
```

**Test Not Starting**
- Check API key validity
- Verify candidate email
- Check provider status

**Results Not Loading**
- Wait for test completion
- Check session ID
- Verify provider connection

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test provider connection
from app.services.external_assessment_service import HackerRankProvider

provider = HackerRankProvider()
tests = await provider.get_available_tests()
print(tests)
```

---

## 📈 Analytics

### Track Metrics
- Test completion rates
- Average scores by provider
- Time to complete
- Pass/fail rates

### Reports
- Candidate performance
- Provider comparison
- ROI analysis
- Skill gap analysis

---

## 🔄 Updates & Maintenance

### Provider Updates
- Monitor provider API changes
- Update integration code
- Test after updates

### Feature Requests
- Request new providers
- Suggest improvements
- Report bugs

---

## 📞 Support

### Provider Support
- **HackerRank**: support@hackerrank.com
- **CodeSignal**: support@codesignal.com
- **TestGorilla**: support@testgorilla.com
- **Pluralsight**: support@pluralsight.com

### Platform Support
- Check documentation
- Review API docs
- Contact development team

---

## 🎉 Benefits

### For Candidates
✅ Industry-recognized certifications
✅ Skill validation
✅ Career advancement
✅ Competitive advantage

### For Companies
✅ Standardized evaluation
✅ Reduced hiring time
✅ Better candidate quality
✅ Data-driven decisions

### For Platform
✅ Enhanced credibility
✅ Competitive advantage
✅ Revenue opportunities
✅ User satisfaction

---

## 🚀 Future Enhancements

### Planned Features
- [ ] More providers (Codility, Mettl, etc.)
- [ ] Custom test creation
- [ ] Proctoring integration
- [ ] Video assessments
- [ ] Adaptive testing
- [ ] Skill benchmarking
- [ ] Team assessments
- [ ] Mobile app support

---

## 📝 Conclusion

The external assessments integration provides a comprehensive solution for skill evaluation using industry-standard tests. With support for multiple providers and seamless integration, both candidates and companies benefit from professional, reliable assessments.

**Ready to use!** 🎓
