interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class Cache {
  private cache = new Map<string, CacheItem<any>>();
  private maxSize: number;

  constructor(maxSize = 100) {
    this.maxSize = maxSize;
  }

  set<T>(key: string, data: T, ttl = 5 * 60 * 1000): void {
    // Remove oldest items if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // Check if item has expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    const item = this.cache.get(key);
    
    if (!item) {
      return false;
    }

    // Check if item has expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }

  // Clean up expired items
  cleanup(): void {
    const now = Date.now();
    const entries = Array.from(this.cache.entries());
    entries.forEach(([key, item]) => {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key);
      }
    });
  }
}

// Global cache instance
export const cache = new Cache();

// Cleanup expired items every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(() => {
    cache.cleanup();
  }, 5 * 60 * 1000);
}

// Cache utilities
export const cacheUtils = {
  // Generate cache key from URL and params
  generateKey: (url: string, params?: Record<string, any>): string => {
    const paramString = params ? JSON.stringify(params) : '';
    return `${url}${paramString}`;
  },

  // Cached fetch function
  cachedFetch: async <T>(
    url: string,
    options?: RequestInit,
    ttl?: number
  ): Promise<T> => {
    const key = cacheUtils.generateKey(url, options);
    
    // Check cache first
    const cached = cache.get<T>(key);
    if (cached) {
      return cached;
    }

    // Fetch from network
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Cache the result
    cache.set(key, data, ttl);
    
    return data;
  },

  // Invalidate cache by pattern
  invalidatePattern: (pattern: string): void => {
    const keys = Array.from((cache as any).cache.keys()) as string[];
    keys.forEach(key => {
      if (key.includes(pattern)) {
        cache.delete(key);
      }
    });
  },
};