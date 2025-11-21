import { useEffect, useState } from 'react';

interface AccessibilityPreferences {
  reduceMotion: boolean;
  highContrast: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  screenReader: boolean;
}

export const useAccessibility = () => {
  const [preferences, setPreferences] = useState<AccessibilityPreferences>({
    reduceMotion: false,
    highContrast: false,
    fontSize: 'medium',
    screenReader: false
  });

  useEffect(() => {
    // Check for system preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
    
    // Check for screen reader
    const hasScreenReader = window.navigator.userAgent.includes('NVDA') || 
                           window.navigator.userAgent.includes('JAWS') || 
                           window.speechSynthesis !== undefined;

    // Load saved preferences
    const savedPreferences = localStorage.getItem('accessibility-preferences');
    if (savedPreferences) {
      const parsed = JSON.parse(savedPreferences);
      setPreferences({
        ...parsed,
        reduceMotion: prefersReducedMotion || parsed.reduceMotion,
        highContrast: prefersHighContrast || parsed.highContrast,
        screenReader: hasScreenReader || parsed.screenReader
      });
    } else {
      setPreferences(prev => ({
        ...prev,
        reduceMotion: prefersReducedMotion,
        highContrast: prefersHighContrast,
        screenReader: hasScreenReader
      }));
    }
  }, []);

  useEffect(() => {
    // Apply accessibility preferences to document
    const root = document.documentElement;
    
    if (preferences.reduceMotion) {
      root.classList.add('reduce-motion');
    } else {
      root.classList.remove('reduce-motion');
    }

    if (preferences.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    root.classList.remove('font-small', 'font-medium', 'font-large', 'font-extra-large');
    root.classList.add(`font-${preferences.fontSize}`);

    // Save preferences
    localStorage.setItem('accessibility-preferences', JSON.stringify(preferences));
  }, [preferences]);

  const updatePreference = <K extends keyof AccessibilityPreferences>(
    key: K,
    value: AccessibilityPreferences[K]
  ) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  return {
    preferences,
    updatePreference
  };
};