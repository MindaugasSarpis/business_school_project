import { useState } from 'react';
import SwitcherThree from '../../premade_components/Switchers/SwitcherThree';
import { useMapFilters } from '../../hooks/useMapFilters';
import DropdownDefault from '../../premade_components/Dropdowns/DropdownDefault';

export const MapFilters = () => {
  const { fatalitiesOnly, setFilters } = useMapFilters();

  return (
    <div className="flex w-full justify-start my-2 align-middle">
      <div>
        <span
          className={`${
            fatalitiesOnly == 'yes' ? 'text-blue-400' : ''
          } cursor-pointer m-4`}
          onClick={() => setFilters({ fatalitiesOnly: 'yes' })}
        >
          {' '}
          Show only fatal
        </span>
        <span
          className={`${
            fatalitiesOnly !== 'yes' ? 'text-blue-400' : ''
          } cursor-pointer m-4`}
          onClick={() => setFilters({ fatalitiesOnly: 'no' })}
        >
          {' '}
          Show all
        </span>
      </div>
    </div>
  );
};
