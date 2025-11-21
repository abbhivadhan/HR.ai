import { useState, useEffect, useCallback, useRef } from 'react';

interface UseInfiniteScrollOptions {
  threshold?: number;
  rootMargin?: string;
  hasMore: boolean;
  loading: boolean;
}

export const useInfiniteScroll = (
  fetchMore: () => void,
  options: UseInfiniteScrollOptions
) => {
  const { threshold = 1.0, rootMargin = '0px', hasMore, loading } = options;
  const [isFetching, setIsFetching] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && hasMore && !loading && !isFetching) {
        setIsFetching(true);
        fetchMore();
      }
    },
    [fetchMore, hasMore, loading, isFetching]
  );

  useEffect(() => {
    const element = loadMoreRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(handleObserver, {
      threshold,
      rootMargin,
    });

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [handleObserver, threshold, rootMargin]);

  useEffect(() => {
    if (!loading) {
      setIsFetching(false);
    }
  }, [loading]);

  return { loadMoreRef, isFetching };
};