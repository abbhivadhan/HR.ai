import { useState, useEffect } from 'react';

// Simple translation hook for App Router compatibility
export const useTranslation = (namespace?: string | string[]) => {
  const [currentLocale, setCurrentLocale] = useState('en');
  const [translations, setTranslations] = useState<Record<string, string>>({});

  useEffect(() => {
    // Load translations based on locale
    const loadTranslations = async () => {
      try {
        const response = await fetch(`/locales/${currentLocale}/common.json`);
        if (response.ok) {
          const data = await response.json();
          setTranslations(data);
        }
      } catch (error) {
        console.warn('Failed to load translations:', error);
      }
    };

    loadTranslations();
  }, [currentLocale]);

  const t = (key: string, fallback?: string) => {
    return translations[key] || fallback || key;
  };

  const changeLanguage = (locale: string) => {
    setCurrentLocale(locale);
    localStorage.setItem('preferred-language', locale);
  };

  const formatDate = (date: Date, options?: Intl.DateTimeFormatOptions) => {
    return new Intl.DateTimeFormat(currentLocale, options).format(date);
  };

  const formatNumber = (number: number, options?: Intl.NumberFormatOptions) => {
    return new Intl.NumberFormat(currentLocale, options).format(number);
  };

  const formatCurrency = (amount: number, currency = 'USD') => {
    return new Intl.NumberFormat(currentLocale, {
      style: 'currency',
      currency,
    }).format(amount);
  };

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    const rtf = new Intl.RelativeTimeFormat(currentLocale, { numeric: 'auto' });
    
    if (diffInSeconds < 60) {
      return rtf.format(-diffInSeconds, 'second');
    } else if (diffInSeconds < 3600) {
      return rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
    } else if (diffInSeconds < 86400) {
      return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
    } else {
      return rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
    }
  };

  return {
    t,
    changeLanguage,
    formatDate,
    formatNumber,
    formatCurrency,
    formatRelativeTime,
    currentLocale,
    isRTL: ['ar', 'he', 'fa'].includes(currentLocale),
  };
};