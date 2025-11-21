/**
 * AI-HR Platform JavaScript/Node.js SDK
 * 
 * Official JavaScript client library for the AI-HR Platform API.
 */

export { AIHRClient } from './client';
export * from './types';
export * from './exceptions';

// Re-export commonly used types
export type {
  User,
  Assessment,
  Job,
  JobMatch,
  Interview,
  Webhook,
  APIUsageStats
} from './types';

// Re-export exceptions
export {
  AIHRException,
  AuthenticationError,
  ValidationError,
  NotFoundError,
  RateLimitError,
  ServerError
} from './exceptions';