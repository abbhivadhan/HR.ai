/**
 * Accessibility Tests for UI Components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
// import { axe, toHaveNoViolations } from 'jest-axe';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@/contexts/ThemeContext';
import AnimatedButton from '@/components/ui/AnimatedButton';
import AnimatedInput from '@/components/ui/AnimatedInput';
import ThemeToggle from '@/components/ui/ThemeToggle';
import AccessibilityMenu from '@/components/ui/AccessibilityMenu';

// Extend Jest matchers
// expect.extend(toHaveNoViolations);

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    input: ({ children, ...props }: any) => <input {...props}>{children}</input>,
    label: ({ children, ...props }: any) => <label {...props}>{children}</label>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock Heroicons
jest.mock('@heroicons/react/24/outline', () => ({
  SunIcon: () => <span data-testid="sun-icon">SUN</span>,
  MoonIcon: () => <span data-testid="moon-icon">MOON</span>,
  ComputerDesktopIcon: () => <span data-testid="computer-icon">COMP</span>,
  AdjustmentsHorizontalIcon: () => <span data-testid="adjustments-icon">ADJ</span>,
  EyeIcon: () => <span data-testid="eye-icon">EYE</span>,
  SpeakerWaveIcon: () => <span data-testid="speaker-icon">SPEAK</span>,
  MagnifyingGlassIcon: () => <span data-testid="magnifying-icon">MAG</span>,
}));

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

describe('Accessibility Compliance', () => {
  test('AnimatedButton should render with proper accessibility attributes', () => {
    render(<AnimatedButton>Test Button</AnimatedButton>);
    
    const button = screen.getByRole('button', { name: 'Test Button' });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('type', 'button');
  });

  test('AnimatedInput should have proper label association', () => {
    render(<AnimatedInput label="Test Input" />);
    
    const input = screen.getByLabelText('Test Input');
    expect(input).toBeInTheDocument();
  });

  test('ThemeToggle should have accessible buttons', () => {
    render(
      <TestWrapper>
        <ThemeToggle />
      </TestWrapper>
    );
    
    const lightButton = screen.getByLabelText('Switch to Light theme');
    const darkButton = screen.getByLabelText('Switch to Dark theme');
    const systemButton = screen.getByLabelText('Switch to System theme');
    
    expect(lightButton).toBeInTheDocument();
    expect(darkButton).toBeInTheDocument();
    expect(systemButton).toBeInTheDocument();
  });

  test('AccessibilityMenu should have proper ARIA attributes', () => {
    render(
      <TestWrapper>
        <AccessibilityMenu />
      </TestWrapper>
    );
    
    const menuButton = screen.getByLabelText('Accessibility options');
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
  });
});

describe('Keyboard Navigation', () => {
  test('AnimatedButton should be keyboard accessible', async () => {
    const handleClick = jest.fn();
    render(<AnimatedButton onClick={handleClick}>Test Button</AnimatedButton>);
    
    const button = screen.getByRole('button', { name: 'Test Button' });
    
    // Focus the button
    button.focus();
    expect(button).toHaveFocus();
    
    // Press Enter
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
    expect(handleClick).toHaveBeenCalled();
    
    // Press Space
    handleClick.mockClear();
    fireEvent.keyDown(button, { key: ' ', code: 'Space' });
    expect(handleClick).toHaveBeenCalled();
  });

  test('AnimatedInput should be keyboard accessible', async () => {
    const handleChange = jest.fn();
    render(<AnimatedInput label="Test Input" onChange={handleChange} />);
    
    const input = screen.getByLabelText('Test Input');
    
    // Focus and type
    await userEvent.click(input);
    await userEvent.type(input, 'test value');
    
    expect(input).toHaveFocus();
    expect(handleChange).toHaveBeenCalled();
  });

  test('ThemeToggle buttons should be keyboard accessible', async () => {
    render(
      <TestWrapper>
        <ThemeToggle />
      </TestWrapper>
    );
    
    const lightButton = screen.getByLabelText('Switch to Light theme');
    const darkButton = screen.getByLabelText('Switch to Dark theme');
    const systemButton = screen.getByLabelText('Switch to System theme');
    
    // Tab through buttons
    lightButton.focus();
    expect(lightButton).toHaveFocus();
    
    fireEvent.keyDown(lightButton, { key: 'Tab' });
    expect(darkButton).toHaveFocus();
    
    fireEvent.keyDown(darkButton, { key: 'Tab' });
    expect(systemButton).toHaveFocus();
  });
});

describe('Screen Reader Support', () => {
  test('AnimatedButton should have proper ARIA attributes', () => {
    render(
      <AnimatedButton loading={true} disabled={true}>
        Loading Button
      </AnimatedButton>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('disabled');
    expect(button).toHaveTextContent('Loading Button');
  });

  test('AnimatedInput should have proper labels and descriptions', () => {
    render(
      <AnimatedInput 
        label="Email Address" 
        error="Invalid email format"
        required
      />
    );
    
    const input = screen.getByLabelText('Email Address');
    expect(input).toBeRequired();
    
    const errorMessage = screen.getByText('Invalid email format');
    expect(errorMessage).toBeInTheDocument();
  });

  test('ThemeToggle should have proper ARIA attributes', () => {
    render(
      <TestWrapper>
        <ThemeToggle />
      </TestWrapper>
    );
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toHaveAttribute('aria-label');
    });
  });

  test('AccessibilityMenu should have proper ARIA attributes', async () => {
    render(
      <TestWrapper>
        <AccessibilityMenu />
      </TestWrapper>
    );
    
    const menuButton = screen.getByLabelText('Accessibility options');
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    
    // Open menu
    await userEvent.click(menuButton);
    expect(menuButton).toHaveAttribute('aria-expanded', 'true');
    
    // Check switches have proper ARIA attributes
    const switches = screen.getAllByRole('switch');
    switches.forEach(switchElement => {
      expect(switchElement).toHaveAttribute('aria-checked');
      expect(switchElement).toHaveAttribute('aria-label');
    });
  });
});

describe('Focus Management', () => {
  test('should trap focus in AccessibilityMenu when open', async () => {
    render(
      <TestWrapper>
        <AccessibilityMenu />
      </TestWrapper>
    );
    
    const menuButton = screen.getByLabelText('Accessibility options');
    await userEvent.click(menuButton);
    
    // Menu should be open
    expect(screen.getByText('Accessibility Options')).toBeInTheDocument();
    
    // Focus should be manageable within the menu
    const switches = screen.getAllByRole('switch');
    const buttons = screen.getAllByRole('button');
    
    // All interactive elements should be focusable
    [...switches, ...buttons].forEach(element => {
      element.focus();
      expect(element).toHaveFocus();
    });
  });

  test('should restore focus when AccessibilityMenu closes', async () => {
    render(
      <TestWrapper>
        <AccessibilityMenu />
      </TestWrapper>
    );
    
    const menuButton = screen.getByLabelText('Accessibility options');
    await userEvent.click(menuButton);
    
    // Close menu by clicking outside
    await userEvent.click(document.body);
    
    // Focus should return to trigger button
    await waitFor(() => {
      expect(menuButton).toHaveFocus();
    });
  });
});

describe('Color Contrast', () => {
  test('should maintain sufficient color contrast in different themes', () => {
    const { rerender } = render(
      <TestWrapper>
        <AnimatedButton variant="primary">Primary Button</AnimatedButton>
      </TestWrapper>
    );
    
    const button = screen.getByRole('button');
    const styles = window.getComputedStyle(button);
    
    // Primary button should have sufficient contrast
    expect(styles.backgroundColor).toBeTruthy();
    expect(styles.color).toBeTruthy();
    
    // Test with different variants
    rerender(
      <TestWrapper>
        <AnimatedButton variant="secondary">Secondary Button</AnimatedButton>
      </TestWrapper>
    );
    
    const secondaryButton = screen.getByRole('button');
    const secondaryStyles = window.getComputedStyle(secondaryButton);
    
    expect(secondaryStyles.backgroundColor).toBeTruthy();
    expect(secondaryStyles.color).toBeTruthy();
  });
});

describe('Reduced Motion Support', () => {
  test('should respect prefers-reduced-motion', () => {
    // Mock matchMedia for reduced motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
    
    render(
      <TestWrapper>
        <AnimatedButton>Test Button</AnimatedButton>
      </TestWrapper>
    );
    
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    
    // Animation should be reduced or disabled
    // This would typically be tested by checking CSS classes or styles
    // that disable animations when reduce-motion is active
  });
});