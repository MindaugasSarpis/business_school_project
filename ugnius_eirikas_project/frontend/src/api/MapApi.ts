import axios from 'axios';
import { MarkerDetails } from '../components/map/TrafficMap';

export type MapFilters = {
  fatalitiesOnly?: string;
};

export const fetchMapData = async (
  options?: MapFilters,
): Promise<MarkerDetails[]> => {
  const res = await axios.get('http://localhost:8000/api/mapData');
  let filteredMapData = await res.data;
  console.log(options, 'options');

  if (options?.fatalitiesOnly == 'yes') {
    console.log('here with correct filter');

    filteredMapData = filteredMapData.filter((market: MarkerDetails) => {
      return market.zuvusiuSkaicius > 0;
    });
  }
  console.log('here', filteredMapData);

  return filteredMapData;
};
