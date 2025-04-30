import { useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MapFilters } from '../api/MapApi';

export function useMapFilters() {
  const [searchParams, setSearchParams] = useSearchParams();
  const fatalitiesOnly = searchParams.get(
    'fatalitiesOnly',
  ) as MapFilters['fatalitiesOnly'];

  const setFilters = useCallback((filters: MapFilters) => {
    console.log('setFilters', filters);

    setSearchParams((params) => {
      if (filters.fatalitiesOnly) {
        params.set('fatalitiesOnly', filters.fatalitiesOnly);
      }
      return params;
    });
  }, []);

  return {
    fatalitiesOnly,
    setFilters,
  };
}
