'use client'

import { useState, useEffect } from 'react'

interface BreakpointConfig {
  sm: number
  md: number
  lg: number
  xl: number
  '2xl': number
}

const defaultBreakpoints: BreakpointConfig = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
}

export function useResponsive(breakpoints: Partial<BreakpointConfig> = {}) {
  const config = { ...defaultBreakpoints, ...breakpoints }
  
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  })

  useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      })
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const isMobile = windowSize.width < config.md
  const isTablet = windowSize.width >= config.md && windowSize.width < config.lg
  const isDesktop = windowSize.width >= config.lg

  const breakpoint = {
    isSm: windowSize.width >= config.sm,
    isMd: windowSize.width >= config.md,
    isLg: windowSize.width >= config.lg,
    isXl: windowSize.width >= config.xl,
    is2xl: windowSize.width >= config['2xl'],
  }

  return {
    windowSize,
    isMobile,
    isTablet,
    isDesktop,
    breakpoint,
    width: windowSize.width,
    height: windowSize.height,
  }
}

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const media = window.matchMedia(query)
    setMatches(media.matches)

    const listener = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }

    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}