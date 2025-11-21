/**
 * AI-HR Platform SDK Exceptions
 * 
 * Custom error classes for the AI-HR Platform SDK.
 */

/**
 * Base exception for AI-HR Platform SDK
 */
export class AIHRException extends Error {
  public readonly statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'AIHRException';
    this.statusCode = statusCode;
    
    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AIHRException);
    }
  }
}

/**
 * Authentication failed
 */
export class AuthenticationError extends AIHRException {
  constructor(message: string = 'Authentication failed') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

/**
 * Authorization failed
 */
export class AuthorizationError extends AIHRException {
  constructor(message: string = 'Insufficient permissions') {
    super(message, 403);
    this.name = 'AuthorizationError';
  }
}

/**
 * Resource not found
 */
export class NotFoundError extends AIHRException {
  constructor(message: string = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

/**
 * Request validation failed
 */
export class ValidationError extends AIHRException {
  public readonly errors?: Array<Record<string, any>>;

  constructor(message: string = 'Validation failed', errors?: Array<Record<string, any>>) {
    super(message, 422);
    this.name = 'ValidationError';
    this.errors = errors;
  }
}

/**
 * Rate limit exceeded
 */
export class RateLimitError extends AIHRException {
  public readonly retryAfter: number;

  constructor(message: string = 'Rate limit exceeded', retryAfter: number = 60) {
    super(message, 429);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }
}

/**
 * Server error
 */
export class ServerError extends AIHRException {
  constructor(message: string = 'Internal server error') {
    super(message, 500);
    this.name = 'ServerError';
  }
}

/**
 * Request timeout
 */
export class TimeoutError extends AIHRException {
  constructor(message: string = 'Request timeout') {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Connection error
 */
export class ConnectionError extends AIHRException {
  constructor(message: string = 'Connection error') {
    super(message);
    this.name = 'ConnectionError';
  }
}