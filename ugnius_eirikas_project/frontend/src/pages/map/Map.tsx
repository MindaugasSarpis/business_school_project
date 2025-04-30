import TrafficMap from '../../components/map/TrafficMap';
import { Layout } from '../../layout/Layout';
import { MapFilters } from './Filters';

export const Map = () => {
  return (
    <Layout>
      <div className="h-full w-full">
        Map page
        <MapFilters />
        <div className="h-screen w-xl">
          <TrafficMap />
        </div>
      </div>
    </Layout>
  );
};
