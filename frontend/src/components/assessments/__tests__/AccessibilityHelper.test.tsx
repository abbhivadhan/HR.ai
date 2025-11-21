import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AccessibilityHelper from '../AccessibilityHelper';

describe('AccessibilityHelper', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should not render when not visible', () => {
    render(<AccessibilityHelper isVisible={false} onClose={mockOnClose} />);
    
    expect(screen.queryByText('Accessibility Settings & Help')).not.toBeInTheDocument();
  });

  it('should render when visible', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('Accessibility Settings & Help')).toBeInTheDocument();
    expect(screen.getByText('Visual Settings')).toBeInTheDocument();
    expect(screen.getByText('Keyboard Shortcuts')).toBeInTheDocument();
    expect(screen.getByText('Screen Reader Tips')).toBeInTheDocument();
    expect(screen.getByText('Navigation Tips')).toBeInTheDocument();
  });

  it('should have proper ARIA attributes', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'accessibility-title');
  });

  it('should handle font size changes', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    const fontSizeSlider = screen.getByLabelText(/Font Size:/);
    fireEvent.change(fontSizeSlider, { target: { value: '20' } });
    
    expect(fontSizeSlider).toHaveValue('20');
    expect(screen.getByText('Font Size: 20px')).toBeInTheDocument();
  });

  it('should handle high contrast toggle', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    const highContrastCheckbox = screen.getByLabelText('High contrast mode');
    fireEvent.click(highContrastCheckbox);
    
    expect(highContrastCheckbox).toBeChecked();
  });

  it('should handle reduced motion toggle', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    const reducedMotionCheckbox = screen.getByLabelText('Reduce animations and motion');
    fireEvent.click(reducedMotionCheckbox);
    
    expect(reducedMotionCheckbox).toBeChecked();
  });

  it('should display keyboard shortcuts', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    expect(screen.getByText('Toggle fullscreen mode')).toBeInTheDocument();
    expect(screen.getByText('F11')).toBeInTheDocument();
    expect(screen.getByText('Focus on timer')).toBeInTheDocument();
    expect(screen.getByText('Alt + T')).toBeInTheDocument();
  });

  it('should close when close button is clicked', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    const closeButtons = screen.getAllByText('Close');
    fireEvent.click(closeButtons[0]); // Click the first close button
    
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should close when X button is clicked', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    const xButton = screen.getByLabelText('Close accessibility helper');
    fireEvent.click(xButton);
    
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should display screen reader tips', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    expect(screen.getByText(/Questions are announced automatically/)).toBeInTheDocument();
    expect(screen.getByText(/Timer warnings are announced/)).toBeInTheDocument();
    expect(screen.getByText(/All interactive elements have proper labels/)).toBeInTheDocument();
  });

  it('should display navigation tips', () => {
    render(<AccessibilityHelper isVisible={true} onClose={mockOnClose} />);
    
    expect(screen.getByText(/Use Tab to move between interactive elements/)).toBeInTheDocument();
    expect(screen.getByText(/Use Shift\+Tab to move backwards/)).toBeInTheDocument();
    expect(screen.getByText(/Focus indicators show which element/)).toBeInTheDocument();
  });
});