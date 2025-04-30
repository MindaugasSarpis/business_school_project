import ChartCarTypes from '../../components/analysis/ChartCarTypes';
import ChartDeaths from '../../components/analysis/ChartDeaths';
import ChartSober from '../../components/analysis/ChartSober';
import { StatsRow } from '../../components/analysis/StatsRow';
import { Layout } from '../../layout/Layout';
export const AnalysisPage = () => {
  return (
    <Layout>
      <div>
        Select the period:
        <select
          name=""
          id=""
          className="relative z-20 inline-flex appearance-none bg-transparent py-1 pl-3 pr-8 text-sm font-medium outline-none"
        >
          <option value="" className="dark:bg-boxdark">
            2023
          </option>
          <option value="" className="dark:bg-boxdark">
            2022
          </option>
        </select>
      </div>
      <StatsRow />

      <div className="my-5">
        <ChartDeaths />
      </div>
      <div className="grid grid-cols-5 gap-2 md:gap-1 2xl:gap-2">
        <div className="col-span-3">
          <ChartCarTypes />
        </div>
        <div className="col-span-2">
          <ChartSober />
          <div />
        </div>
      </div>
    </Layout>
  );
};
