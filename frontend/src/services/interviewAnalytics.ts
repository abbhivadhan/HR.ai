// Real-time interview analytics service
// Analyzes spoken responses and provides genuine feedback

interface AnalysisResult {
  relevanceScore: number
  clarityScore: number
  completenessScore: number
  professionalismScore: number
  overallScore: number
  wordCount: number
  speakingRate: number
  fillerWordCount: number
  keywordsMatched: string[]
  strengths: string[]
  improvements: string[]
  detailedFeedback: string
}

export class InterviewAnalytics {
  private fillerWords = [
    'um', 'uh', 'like', 'you know', 'sort of', 'kind of',
    'basically', 'actually', 'literally', 'just', 'really',
    'very', 'so', 'well', 'i mean', 'you see'
  ]

  private technicalKeywords = [
    'algorithm', 'database', 'api', 'framework', 'architecture',
    'testing', 'deployment', 'optimization', 'scalability', 'security',
    'performance', 'debugging', 'refactoring', 'documentation', 'agile',
    'scrum', 'git', 'ci/cd', 'microservices', 'cloud'
  ]

  /**
   * Analyze a candidate's response to an interview question
   */
  analyzeResponse(
    question: string,
    answer: string,
    duration: number, // in seconds
    questionType: string
  ): AnalysisResult {
    const words = this.tokenize(answer)
    const questionWords = this.tokenize(question)
    
    // Calculate basic metrics
    const wordCount = words.length
    const speakingRate = duration > 0 ? (wordCount / duration) * 60 : 0 // words per minute
    const fillerWordCount = this.countFillerWords(answer)
    
    // Extract keywords from question
    const questionKeywords = this.extractKeywords(question, questionType)
    const answerKeywords = this.extractKeywords(answer, questionType)
    const keywordsMatched = this.findMatchingKeywords(questionKeywords, answerKeywords)
    
    // Calculate scores
    const relevanceScore = this.calculateRelevanceScore(
      question,
      answer,
      questionKeywords,
      answerKeywords,
      keywordsMatched
    )
    
    const clarityScore = this.calculateClarityScore(
      answer,
      wordCount,
      fillerWordCount,
      speakingRate
    )
    
    const completenessScore = this.calculateCompletenessScore(
      answer,
      wordCount,
      questionType
    )
    
    const professionalismScore = this.calculateProfessionalismScore(
      answer,
      fillerWordCount,
      wordCount
    )
    
    const overallScore = Math.round(
      (relevanceScore * 0.35 +
       clarityScore * 0.25 +
       completenessScore * 0.25 +
       professionalismScore * 0.15)
    )
    
    // Generate feedback
    const strengths = this.identifyStrengths(
      relevanceScore,
      clarityScore,
      completenessScore,
      professionalismScore,
      wordCount,
      speakingRate,
      keywordsMatched
    )
    
    const improvements = this.identifyImprovements(
      relevanceScore,
      clarityScore,
      completenessScore,
      professionalismScore,
      fillerWordCount,
      wordCount,
      speakingRate
    )
    
    const detailedFeedback = this.generateDetailedFeedback(
      relevanceScore,
      clarityScore,
      completenessScore,
      professionalismScore,
      questionType
    )
    
    return {
      relevanceScore,
      clarityScore,
      completenessScore,
      professionalismScore,
      overallScore,
      wordCount,
      speakingRate: Math.round(speakingRate),
      fillerWordCount,
      keywordsMatched,
      strengths,
      improvements,
      detailedFeedback
    }
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 0)
  }

  private countFillerWords(text: string): number {
    const lowerText = text.toLowerCase()
    return this.fillerWords.reduce((count, filler) => {
      const regex = new RegExp(`\\b${filler}\\b`, 'gi')
      const matches = lowerText.match(regex)
      return count + (matches ? matches.length : 0)
    }, 0)
  }

  private extractKeywords(text: string, questionType: string): string[] {
    const words = this.tokenize(text)
    const stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
      'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
      'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
      'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
      'who', 'when', 'where', 'why', 'how', 'tell', 'describe', 'explain'
    ])
    
    // Filter out stop words and short words
    const keywords = words.filter(word => 
      !stopWords.has(word) && word.length > 3
    )
    
    // For technical questions, prioritize technical keywords
    if (questionType === 'technical') {
      const technicalFound = keywords.filter(word =>
        this.technicalKeywords.some(tech => word.includes(tech) || tech.includes(word))
      )
      const uniqueSet = new Set([...technicalFound, ...keywords])
      return Array.from(uniqueSet)
    }
    
    const uniqueSet = new Set(keywords)
    return Array.from(uniqueSet)
  }

  private findMatchingKeywords(questionKeywords: string[], answerKeywords: string[]): string[] {
    const matches: string[] = []
    
    for (const qKeyword of questionKeywords) {
      for (const aKeyword of answerKeywords) {
        // Exact match
        if (qKeyword === aKeyword) {
          matches.push(qKeyword)
        }
        // Partial match (one contains the other)
        else if (qKeyword.includes(aKeyword) || aKeyword.includes(qKeyword)) {
          matches.push(qKeyword)
        }
        // Similar words (simple similarity check)
        else if (this.areSimilar(qKeyword, aKeyword)) {
          matches.push(qKeyword)
        }
      }
    }
    
    const uniqueMatches = new Set(matches)
    return Array.from(uniqueMatches)
  }

  private areSimilar(word1: string, word2: string): boolean {
    // Simple similarity check based on common prefix
    if (word1.length < 4 || word2.length < 4) return false
    
    const minLength = Math.min(word1.length, word2.length)
    const prefix = Math.floor(minLength * 0.7)
    
    return word1.substring(0, prefix) === word2.substring(0, prefix)
  }

  private calculateRelevanceScore(
    question: string,
    answer: string,
    questionKeywords: string[],
    answerKeywords: string[],
    keywordsMatched: string[]
  ): number {
    if (questionKeywords.length === 0) return 70
    
    // Base score from keyword matching
    const keywordMatchRatio = keywordsMatched.length / questionKeywords.length
    let score = keywordMatchRatio * 60
    
    // Bonus for answer length (shows engagement)
    const words = this.tokenize(answer)
    if (words.length > 30) score += 15
    else if (words.length > 15) score += 10
    else if (words.length > 5) score += 5
    
    // Bonus for specific examples (contains "example", "instance", "time when")
    if (/example|instance|time when|situation where/i.test(answer)) {
      score += 10
    }
    
    // Bonus for structured answer (contains "first", "second", "finally")
    if (/first|second|third|finally|lastly/i.test(answer)) {
      score += 10
    }
    
    // Penalty for very short answers
    if (words.length < 10) score -= 20
    
    return Math.max(0, Math.min(100, Math.round(score)))
  }

  private calculateClarityScore(
    answer: string,
    wordCount: number,
    fillerWordCount: number,
    speakingRate: number
  ): number {
    let score = 100
    
    // Penalty for excessive filler words
    const fillerRatio = wordCount > 0 ? fillerWordCount / wordCount : 0
    if (fillerRatio > 0.15) score -= 30
    else if (fillerRatio > 0.10) score -= 20
    else if (fillerRatio > 0.05) score -= 10
    
    // Penalty for speaking too fast or too slow
    if (speakingRate > 180) score -= 15 // Too fast
    else if (speakingRate < 100 && speakingRate > 0) score -= 15 // Too slow
    
    // Bonus for good speaking rate (120-160 wpm is ideal)
    if (speakingRate >= 120 && speakingRate <= 160) score += 10
    
    // Check for sentence structure (periods, commas indicate structure)
    const sentences = answer.split(/[.!?]+/).filter(s => s.trim().length > 0)
    if (sentences.length > 2) score += 10
    
    return Math.max(0, Math.min(100, Math.round(score)))
  }

  private calculateCompletenessScore(
    answer: string,
    wordCount: number,
    questionType: string
  ): number {
    let score = 50 // Base score
    
    // Score based on word count (varies by question type)
    const minWords = questionType === 'introduction' ? 40 : 30
    const idealWords = questionType === 'introduction' ? 80 : 60
    
    if (wordCount >= idealWords) score += 40
    else if (wordCount >= minWords) score += 30
    else if (wordCount >= minWords * 0.7) score += 20
    else score += 10
    
    // Bonus for providing examples
    if (/for example|such as|like when|instance/i.test(answer)) {
      score += 10
    }
    
    // Bonus for showing depth (technical terms, specific details)
    const hasDetails = /specifically|particularly|detail|process|method|approach/i.test(answer)
    if (hasDetails) score += 10
    
    return Math.max(0, Math.min(100, Math.round(score)))
  }

  private calculateProfessionalismScore(
    answer: string,
    fillerWordCount: number,
    wordCount: number
  ): number {
    let score = 100
    
    // Check for professional language
    const unprofessionalWords = ['gonna', 'wanna', 'gotta', 'yeah', 'nah', 'stuff', 'things']
    const hasUnprofessional = unprofessionalWords.some(word => 
      new RegExp(`\\b${word}\\b`, 'i').test(answer)
    )
    if (hasUnprofessional) score -= 15
    
    // Penalty for excessive filler words
    const fillerRatio = wordCount > 0 ? fillerWordCount / wordCount : 0
    if (fillerRatio > 0.10) score -= 20
    
    // Bonus for professional phrases
    const professionalPhrases = [
      'experience', 'responsibility', 'achievement', 'challenge',
      'solution', 'result', 'impact', 'collaboration', 'leadership'
    ]
    const professionalCount = professionalPhrases.filter(phrase =>
      new RegExp(`\\b${phrase}`, 'i').test(answer)
    ).length
    score += Math.min(20, professionalCount * 5)
    
    return Math.max(0, Math.min(100, Math.round(score)))
  }

  private identifyStrengths(
    relevanceScore: number,
    clarityScore: number,
    completenessScore: number,
    professionalismScore: number,
    wordCount: number,
    speakingRate: number,
    keywordsMatched: string[]
  ): string[] {
    const strengths: string[] = []
    
    if (relevanceScore >= 80) {
      strengths.push('Directly addressed the question with relevant information')
    }
    
    if (clarityScore >= 80) {
      strengths.push('Communicated clearly with minimal filler words')
    }
    
    if (completenessScore >= 80) {
      strengths.push('Provided comprehensive and detailed response')
    }
    
    if (professionalismScore >= 85) {
      strengths.push('Maintained professional tone throughout')
    }
    
    if (speakingRate >= 120 && speakingRate <= 160) {
      strengths.push('Excellent speaking pace - clear and easy to follow')
    }
    
    if (wordCount >= 50) {
      strengths.push('Provided substantial content in response')
    }
    
    if (keywordsMatched.length >= 3) {
      strengths.push('Covered key topics from the question')
    }
    
    if (strengths.length === 0) {
      strengths.push('Attempted to answer the question')
    }
    
    return strengths
  }

  private identifyImprovements(
    relevanceScore: number,
    clarityScore: number,
    completenessScore: number,
    professionalismScore: number,
    fillerWordCount: number,
    wordCount: number,
    speakingRate: number
  ): string[] {
    const improvements: string[] = []
    
    if (relevanceScore < 70) {
      improvements.push('Focus more on directly answering the specific question asked')
    }
    
    if (clarityScore < 70) {
      improvements.push('Reduce filler words (um, uh, like) for clearer communication')
    }
    
    if (completenessScore < 70) {
      improvements.push('Provide more detailed examples and specific information')
    }
    
    if (professionalismScore < 75) {
      improvements.push('Use more professional language and terminology')
    }
    
    if (fillerWordCount > wordCount * 0.10) {
      improvements.push('Practice reducing filler words - try pausing instead')
    }
    
    if (speakingRate > 180) {
      improvements.push('Slow down your speaking pace for better clarity')
    } else if (speakingRate < 100 && speakingRate > 0) {
      improvements.push('Increase your speaking pace slightly to maintain engagement')
    }
    
    if (wordCount < 20) {
      improvements.push('Elaborate more on your answers with specific examples')
    }
    
    if (improvements.length === 0) {
      improvements.push('Continue practicing to build confidence')
    }
    
    return improvements
  }

  private generateDetailedFeedback(
    relevanceScore: number,
    clarityScore: number,
    completenessScore: number,
    professionalismScore: number,
    questionType: string
  ): string {
    const avgScore = (relevanceScore + clarityScore + completenessScore + professionalismScore) / 4
    
    let feedback = ''
    
    if (avgScore >= 85) {
      feedback = 'Excellent response! You demonstrated strong communication skills and provided a well-structured, relevant answer. '
    } else if (avgScore >= 70) {
      feedback = 'Good response overall. You addressed the question and communicated effectively. '
    } else if (avgScore >= 55) {
      feedback = 'Decent attempt. Your response touched on relevant points but could be improved. '
    } else {
      feedback = 'Your response needs improvement. Focus on directly answering the question with more detail. '
    }
    
    // Add specific feedback based on scores
    if (relevanceScore < 70) {
      feedback += 'Make sure to directly address all parts of the question. '
    }
    
    if (clarityScore < 70) {
      feedback += 'Work on reducing filler words and speaking more clearly. '
    }
    
    if (completenessScore < 70) {
      feedback += 'Provide more comprehensive answers with specific examples. '
    }
    
    return feedback.trim()
  }
}

// Export singleton instance
export const interviewAnalytics = new InterviewAnalytics()
