'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface LazyImageProps extends Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'onAnimationStart' | 'onAnimationEnd' | 'onLoad' | 'onError'> {
  src: string;
  alt: string;
  placeholder?: string;
  blurDataURL?: string;
  priority?: boolean;
  onLoad?: () => void;
  onError?: () => void;
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholder,
  blurDataURL,
  priority = false,
  onLoad,
  onError,
  className,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    if (priority) return;

    observerRef.current = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observerRef.current?.disconnect();
        }
      },
      { threshold: 0.1, rootMargin: '50px' }
    );

    if (imgRef.current) {
      observerRef.current.observe(imgRef.current);
    }

    return () => {
      observerRef.current?.disconnect();
    };
  }, [priority]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setIsError(true);
    onError?.();
  };

  return (
    <div className={clsx('relative overflow-hidden', className)} ref={imgRef}>
      {/* Placeholder */}
      {!isLoaded && !isError && (
        <motion.div
          className="absolute inset-0 bg-gray-200 dark:bg-gray-700 flex items-center justify-center"
          initial={{ opacity: 1 }}
          animate={{ opacity: isLoaded ? 0 : 1 }}
          transition={{ duration: 0.3 }}
        >
          {blurDataURL ? (
            <img
              src={blurDataURL}
              alt=""
              className="w-full h-full object-cover filter blur-sm scale-110"
            />
          ) : placeholder ? (
            <img
              src={placeholder}
              alt=""
              className="w-full h-full object-cover opacity-50"
            />
          ) : (
            <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded animate-pulse" />
          )}
        </motion.div>
      )}

      {/* Error state */}
      {isError && (
        <div className="absolute inset-0 bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-lg mb-2 mx-auto" />
            <p className="text-sm text-gray-500 dark:text-gray-400">Failed to load image</p>
          </div>
        </div>
      )}

      {/* Actual image */}
      {isInView && (
        <motion.img
          src={src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          className={clsx(
            'w-full h-full object-cover transition-opacity duration-300',
            isLoaded ? 'opacity-100' : 'opacity-0'
          )}
          initial={{ opacity: 0 }}
          animate={{ opacity: isLoaded ? 1 : 0 }}
          transition={{ duration: 0.3 }}
          {...(props as any)}
        />
      )}
    </div>
  );
};

export default LazyImage;