'use client';

import React, { useState, useEffect } from 'react';

interface AccessibilityHelperProps {
  isVisible: boolean;
  onClose: () => void;
}

const AccessibilityHelper: React.FC<AccessibilityHelperProps> = ({ isVisible, onClose }) => {
  const [fontSize, setFontSize] = useState(16);
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    // Apply font size changes
    document.documentElement.style.fontSize = `${fontSize}px`;
  }, [fontSize]);

  useEffect(() => {
    // Apply high contrast mode
    if (highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
  }, [highContrast]);

  useEffect(() => {
    // Apply reduced motion preference
    if (reducedMotion) {
      document.documentElement.classList.add('reduce-motion');
    } else {
      document.documentElement.classList.remove('reduce-motion');
    }
  }, [reducedMotion]);

  const shortcuts = [
    { key: 'F11', description: 'Toggle fullscreen mode' },
    { key: 'Alt + T', description: 'Focus on timer' },
    { key: 'Alt + P', description: 'Announce current progress' },
    { key: 'Alt + H', description: 'Show keyboard shortcuts' },
    { key: 'Ctrl + S', description: 'Save current work (coding questions)' },
    { key: 'Ctrl + Shift + Enter', description: 'Run tests (coding questions)' },
    { key: 'Escape', description: 'Focus on submit button (from text areas)' },
    { key: 'Tab', description: 'Navigate between interactive elements' },
    { key: 'Space/Enter', description: 'Activate buttons and links' },
  ];

  if (!isVisible) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="accessibility-title"
    >
      <div className="bg-white rounded-lg p-6 max-w-2xl max-h-[80vh] overflow-y-auto mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 id="accessibility-title" className="text-xl font-semibold text-gray-900">
            Accessibility Settings & Help
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            aria-label="Close accessibility helper"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-6">
          {/* Visual Settings */}
          <section>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Visual Settings</h3>
            <div className="space-y-4">
              {/* Font Size */}
              <div>
                <label htmlFor="font-size" className="block text-sm font-medium text-gray-700 mb-2">
                  Font Size: {fontSize}px
                </label>
                <input
                  id="font-size"
                  type="range"
                  min="12"
                  max="24"
                  value={fontSize}
                  onChange={(e) => setFontSize(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Small</span>
                  <span>Large</span>
                </div>
              </div>

              {/* High Contrast */}
              <div className="flex items-center">
                <input
                  id="high-contrast"
                  type="checkbox"
                  checked={highContrast}
                  onChange={(e) => setHighContrast(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="high-contrast" className="ml-2 block text-sm text-gray-700">
                  High contrast mode
                </label>
              </div>

              {/* Reduced Motion */}
              <div className="flex items-center">
                <input
                  id="reduced-motion"
                  type="checkbox"
                  checked={reducedMotion}
                  onChange={(e) => setReducedMotion(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="reduced-motion" className="ml-2 block text-sm text-gray-700">
                  Reduce animations and motion
                </label>
              </div>
            </div>
          </section>

          {/* Keyboard Shortcuts */}
          <section>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Keyboard Shortcuts</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid gap-3">
                {shortcuts.map((shortcut, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{shortcut.description}</span>
                    <kbd className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono">
                      {shortcut.key}
                    </kbd>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Screen Reader Tips */}
          <section>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Screen Reader Tips</h3>
            <div className="bg-blue-50 rounded-lg p-4">
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Questions are announced automatically when they change</li>
                <li>• Timer warnings are announced at 5 minutes and 1 minute remaining</li>
                <li>• Progress updates are available with Alt+P</li>
                <li>• All interactive elements have proper labels and descriptions</li>
                <li>• Test results and feedback are announced when available</li>
              </ul>
            </div>
          </section>

          {/* Navigation Tips */}
          <section>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Navigation Tips</h3>
            <div className="bg-green-50 rounded-lg p-4">
              <ul className="text-sm text-green-800 space-y-2">
                <li>• Use Tab to move between interactive elements</li>
                <li>• Use Shift+Tab to move backwards</li>
                <li>• Use arrow keys to navigate between radio button options</li>
                <li>• Use Space or Enter to activate buttons</li>
                <li>• Focus indicators show which element is currently selected</li>
              </ul>
            </div>
          </section>
        </div>

        {/* Close Button */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccessibilityHelper;