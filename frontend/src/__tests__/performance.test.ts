/**
 * Performance Tests for UI/UX Optimizations
 */

import { performanceMonitor, analyzeBundleSize, getMemoryUsage } from '@/utils/performance';
import { cache, cacheUtils } from '@/utils/cache';

// Mock performance API for testing
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  getEntriesByType: jest.fn(() => []),
  memory: {
    usedJSHeapSize: 1024 * 1024 * 10, // 10MB
    totalJSHeapSize: 1024 * 1024 * 20, // 20MB
    jsHeapSizeLimit: 1024 * 1024 * 100, // 100MB
  }
};

// Mock global performance
Object.defineProperty(global, 'performance', {
  value: mockPerformance,
  writable: true
});

describe('Performance Monitoring', () => {
  beforeEach(() => {
    performanceMonitor.clear();
    jest.clearAllMocks();
  });

  test('should record timing metrics', () => {
    performanceMonitor.recordMetric('test_timing', 100, 'timing');
    const metrics = performanceMonitor.getMetrics();
    
    expect(metrics).toHaveLength(1);
    expect(metrics[0].name).toBe('test_timing');
    expect(metrics[0].value).toBe(100);
    expect(metrics[0].type).toBe('timing');
  });

  test('should measure function execution time', () => {
    const testFunction = () => {
      // Simulate some work
      return 'result';
    };

    const result = performanceMonitor.measureFunction('test_function', testFunction);
    
    expect(result).toBe('result');
    expect(mockPerformance.now).toHaveBeenCalledTimes(2);
    
    const metrics = performanceMonitor.getMetrics();
    expect(metrics).toHaveLength(1);
    expect(metrics[0].name).toBe('test_function');
  });

  test('should measure async function execution time', async () => {
    const asyncFunction = async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
      return 'async_result';
    };

    const result = await performanceMonitor.measureAsyncFunction('async_test', asyncFunction);
    
    expect(result).toBe('async_result');
    
    const metrics = performanceMonitor.getMetrics();
    expect(metrics).toHaveLength(1);
    expect(metrics[0].name).toBe('async_test');
  });

  test('should calculate average metrics', () => {
    performanceMonitor.recordMetric('test_metric', 100);
    performanceMonitor.recordMetric('test_metric', 200);
    performanceMonitor.recordMetric('test_metric', 300);
    
    const average = performanceMonitor.getAverageMetric('test_metric');
    expect(average).toBe(200);
  });

  test('should limit metrics to prevent memory leaks', () => {
    // Add more than 100 metrics
    for (let i = 0; i < 150; i++) {
      performanceMonitor.recordMetric(`metric_${i}`, i);
    }
    
    const metrics = performanceMonitor.getMetrics();
    expect(metrics.length).toBeLessThanOrEqual(100);
  });
});

describe('Caching System', () => {
  beforeEach(() => {
    cache.clear();
  });

  test('should store and retrieve cached data', () => {
    const testData = { message: 'test data' };
    cache.set('test_key', testData);
    
    const retrieved = cache.get('test_key');
    expect(retrieved).toEqual(testData);
  });

  test('should respect TTL and expire data', (done) => {
    const testData = { message: 'test data' };
    cache.set('test_key', testData, 50); // 50ms TTL
    
    expect(cache.has('test_key')).toBe(true);
    
    setTimeout(() => {
      expect(cache.has('test_key')).toBe(false);
      expect(cache.get('test_key')).toBeNull();
      done();
    }, 60);
  });

  test('should generate consistent cache keys', () => {
    const url = '/api/test';
    const params = { page: 1, limit: 10 };
    
    const key1 = cacheUtils.generateKey(url, params);
    const key2 = cacheUtils.generateKey(url, params);
    
    expect(key1).toBe(key2);
  });

  test('should handle cache size limits', () => {
    const smallCache = new (cache.constructor as any)(3); // Max 3 items
    
    smallCache.set('key1', 'value1');
    smallCache.set('key2', 'value2');
    smallCache.set('key3', 'value3');
    smallCache.set('key4', 'value4'); // Should evict key1
    
    expect(smallCache.has('key1')).toBe(false);
    expect(smallCache.has('key4')).toBe(true);
    expect(smallCache.size()).toBe(3);
  });
});

describe('Bundle Analysis', () => {
  test('should analyze bundle size when performance entries exist', () => {
    const mockEntries = [
      { name: 'app.js', transferSize: 1024 * 100 }, // 100KB
      { name: 'vendor.js', transferSize: 1024 * 200 }, // 200KB
      { name: 'styles.css', transferSize: 1024 * 50 }, // 50KB
    ];

    mockPerformance.getEntriesByType.mockReturnValue(mockEntries);
    
    const analysis = analyzeBundleSize();
    
    expect(analysis).toEqual({
      totalJSSize: 300, // KB
      totalCSSSize: 50, // KB
      jsFileCount: 2,
      cssFileCount: 1,
    });
  });

  test('should return null when performance API is not available', () => {
    const originalPerformance = global.performance;
    delete (global as any).performance;
    
    const analysis = analyzeBundleSize();
    expect(analysis).toBeNull();
    
    global.performance = originalPerformance;
  });
});

describe('Memory Usage', () => {
  test('should get memory usage when available', () => {
    const memoryInfo = getMemoryUsage();
    
    expect(memoryInfo).toEqual({
      usedJSHeapSize: 10, // MB
      totalJSHeapSize: 20, // MB
      jsHeapSizeLimit: 100, // MB
    });
  });

  test('should return null when memory API is not available', () => {
    const originalMemory = mockPerformance.memory;
    delete mockPerformance.memory;
    
    const memoryInfo = getMemoryUsage();
    expect(memoryInfo).toBeNull();
    
    mockPerformance.memory = originalMemory;
  });
});

describe('Core Web Vitals', () => {
  test('should track core web vitals', () => {
    performanceMonitor.recordMetric('largest_contentful_paint', 2000);
    performanceMonitor.recordMetric('first_input_delay', 50);
    performanceMonitor.recordMetric('cumulative_layout_shift', 0.1);
    
    const vitals = performanceMonitor.getCoreWebVitals();
    
    expect(vitals).toEqual({
      lcp: 2000,
      fid: 50,
      cls: 0.1,
    });
  });

  test('should return 0 for missing vitals', () => {
    // Clear any existing metrics first
    performanceMonitor.clear();
    
    const vitals = performanceMonitor.getCoreWebVitals();
    
    expect(vitals).toEqual({
      lcp: 0,
      fid: 0,
      cls: 0,
    });
  });
});