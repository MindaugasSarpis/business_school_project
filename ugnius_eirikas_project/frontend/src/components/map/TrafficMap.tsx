import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import Loader from '../../common/Loader';
import { useQuery } from '@tanstack/react-query';

import MarkerClusterGroup from 'react-leaflet-cluster';
import { fetchMapData } from '../../api/MapApi';
import { useMapFilters } from '../../hooks/useMapFilters';

export interface MarkerDetails {
  dataLaikas: number;
  dalyviuSkaicius: number;
  zuvusiuSkaicius: number;
  suzeistuSkaicius: number;
  tpSkaicius: number;
  savivaldybe: string;
  gatve: string;
  leistinasGreitis: number;
  lat: number;
  lon: number;
  namas: string;
}

const TrafficMap = () => {
  const { fatalitiesOnly } = useMapFilters();
  const {
    data: mapData,
    isLoading,
    isError,
  } = useQuery({
    queryFn: (): Promise<MarkerDetails[]> => fetchMapData({ fatalitiesOnly }),
    queryKey: ['mapData', '2023', { fatalitiesOnly }],
    staleTime: Infinity,
  });

  if (isLoading)
    return (
      <div>
        <Loader />
      </div>
    );
  if (isError) return <div>Error</div>;

  return (
    <MapContainer
      center={[54.7060538747366, 25.230352337531]}
      zoom={13}
      scrollWheelZoom={true}
      className="map-container h-full w-full"
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      <MarkerClusterGroup chunkedLoading>
        {mapData?.map(
          (item: MarkerDetails, index: number) =>
            item.lat &&
            item.lon && (
              <Marker key={index} position={[item.lat, item.lon]}>
                <Popup>
                  {`${item.savivaldybe ?? ''}  ${item.gatve ?? ''}`} <br />
                  {'Number of injured people: ' + item.suzeistuSkaicius} <br />
                  {'Number of fatalities: ' + item.zuvusiuSkaicius} <br />
                  {'Number of people involved: ' + item.dalyviuSkaicius} <br />
                </Popup>
              </Marker>
            ),
        )}
      </MarkerClusterGroup>
    </MapContainer>
  );
};

export default TrafficMap;
function useProductFilters(): { search: any; category: any; maxPrice: any } {
  throw new Error('Function not implemented.');
}
