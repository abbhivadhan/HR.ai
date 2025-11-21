// Performance monitoring utilities

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  type: 'timing' | 'counter' | 'gauge';
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observers: PerformanceObserver[] = [];

  constructor() {
    if (typeof window !== 'undefined') {
      this.initializeObservers();
    }
  }

  private initializeObservers() {
    // Observe navigation timing
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      const navObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.recordMetric('page_load_time', navEntry.loadEventEnd - navEntry.fetchStart, 'timing');
            this.recordMetric('dom_content_loaded', navEntry.domContentLoadedEventEnd - navEntry.fetchStart, 'timing');
            this.recordMetric('first_paint', navEntry.loadEventEnd - navEntry.fetchStart, 'timing');
          }
        }
      });
      navObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navObserver);

      // Observe resource timing
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'resource') {
            const resourceEntry = entry as PerformanceResourceTiming;
            this.recordMetric(`resource_${resourceEntry.name}`, resourceEntry.duration, 'timing');
          }
        }
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);

      // Observe largest contentful paint
      const lcpObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric('largest_contentful_paint', entry.startTime, 'timing');
        }
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);

      // Observe first input delay
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const fidEntry = entry as any;
          if (fidEntry.processingStart) {
            this.recordMetric('first_input_delay', fidEntry.processingStart - entry.startTime, 'timing');
          }
        }
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);

      // Observe cumulative layout shift
      const clsObserver = new PerformanceObserver((list) => {
        let clsValue = 0;
        for (const entry of list.getEntries()) {
          const clsEntry = entry as any;
          if (!clsEntry.hadRecentInput && clsEntry.value) {
            clsValue += clsEntry.value;
          }
        }
        this.recordMetric('cumulative_layout_shift', clsValue, 'gauge');
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(clsObserver);
    }
  }

  recordMetric(name: string, value: number, type: PerformanceMetric['type'] = 'timing') {
    this.metrics.push({
      name,
      value,
      timestamp: Date.now(),
      type,
    });

    // Keep only last 100 metrics to prevent memory leaks
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }
  }

  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  getMetricsByName(name: string): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.name === name);
  }

  getAverageMetric(name: string): number {
    const metrics = this.getMetricsByName(name);
    if (metrics.length === 0) return 0;
    return metrics.reduce((sum, metric) => sum + metric.value, 0) / metrics.length;
  }

  // Measure function execution time
  measureFunction<T>(name: string, fn: () => T): T {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    this.recordMetric(name, end - start, 'timing');
    return result;
  }

  // Measure async function execution time
  async measureAsyncFunction<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    const result = await fn();
    const end = performance.now();
    this.recordMetric(name, end - start, 'timing');
    return result;
  }

  // Get Core Web Vitals
  getCoreWebVitals() {
    return {
      lcp: this.getAverageMetric('largest_contentful_paint'),
      fid: this.getAverageMetric('first_input_delay'),
      cls: this.getAverageMetric('cumulative_layout_shift'),
    };
  }

  // Export metrics for analysis
  exportMetrics(): string {
    return JSON.stringify(this.metrics, null, 2);
  }

  // Clear all metrics
  clear() {
    this.metrics = [];
  }

  // Cleanup observers
  disconnect() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

// Utility functions
export const measureRender = (componentName: string) => {
  return (target: any, propertyName: string, descriptor: PropertyDescriptor) => {
    const method = descriptor.value;
    descriptor.value = function (...args: any[]) {
      return performanceMonitor.measureFunction(`${componentName}.${propertyName}`, () => {
        return method.apply(this, args);
      });
    };
  };
};

// Bundle size analyzer
export const analyzeBundleSize = () => {
  if (typeof window !== 'undefined' && 'performance' in window) {
    const entries = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    const jsFiles = entries.filter(entry => entry.name.endsWith('.js'));
    const cssFiles = entries.filter(entry => entry.name.endsWith('.css'));
    
    const totalJSSize = jsFiles.reduce((total, file) => total + (file.transferSize || 0), 0);
    const totalCSSSize = cssFiles.reduce((total, file) => total + (file.transferSize || 0), 0);
    
    return {
      totalJSSize: Math.round(totalJSSize / 1024), // KB
      totalCSSSize: Math.round(totalCSSSize / 1024), // KB
      jsFileCount: jsFiles.length,
      cssFileCount: cssFiles.length,
    };
  }
  return null;
};

// Memory usage monitoring
export const getMemoryUsage = () => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    return {
      usedJSHeapSize: Math.round(memory.usedJSHeapSize / 1024 / 1024), // MB
      totalJSHeapSize: Math.round(memory.totalJSHeapSize / 1024 / 1024), // MB
      jsHeapSizeLimit: Math.round(memory.jsHeapSizeLimit / 1024 / 1024), // MB
    };
  }
  return null;
};