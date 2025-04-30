import { ApexOptions } from 'apexcharts';
import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { fetchStatsData } from '../../api/Api';
import { useQuery } from '@tanstack/react-query';
import Loader from '../../common/Loader';
import { CarType, CarTypesData } from '../../interfaces/analysis/Interfaces';

interface ChartCarTypes {
  series: number[];
}

const ChartCarTypes: React.FC = () => {
  const {
    data: carTypesData,
    isLoading,
    isError,
  } = useQuery({
    queryFn: (): Promise<CarTypesData> =>
      fetchStatsData('http://127.0.0.1:8000/api/carType'),
    queryKey: ['carTypes', '2023'],
    staleTime: Infinity,
  });
  const [state, setState] = useState<ChartCarTypes>({
    series: [],
  });

  useEffect(() => {
    if (carTypesData && !isLoading && !isError) {
      setState({
        series: carTypesData.accidents_top.map(
          (item: CarType) => item.total_accidents,
        ),
      });
    }
  }, [carTypesData]);
  if (isLoading)
    return (
      <div>
        <Loader />
      </div>
    );
  if (isError) return <div>Error</div>;
  const options: ApexOptions = {
    chart: {
      fontFamily: 'Satoshi, sans-serif',
      type: 'donut',
    },
    colors: [
      '#3C50E0',
      '#4C60F0',
      '#5C70F1',
      '#6C80F2',
      '#7C90F3',
      '#6CC9CF',
      '#57B8C9',
      '#50A7C2',
      '#4A96BB',
      '#4385B4',
    ],

    labels: carTypesData?.accidents_top.map((item) => item.marke),
    legend: {
      show: false,
      position: 'bottom',
    },

    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          background: 'transparent',
        },
      },
    },
    dataLabels: {
      enabled: true,
    },
    responsive: [
      {
        breakpoint: 2600,
        options: {
          chart: {
            width: 380,
          },
        },
      },
      {
        breakpoint: 640,
        options: {
          chart: {
            width: 200,
          },
        },
      },
    ],
  };
  return (
    <div className="sm:px-7.5 col-span-12 rounded-sm border border-stroke bg-white px-5 pb-5 pt-7.5 shadow-default dark:border-strokedark dark:bg-boxdark xl:col-span-5">
      <div className="mb-3 justify-between gap-4 sm:flex">
        <div>
          <h5 className="text-xl font-semibold text-black dark:text-white">
            Top car types by:
            <select
              name=""
              id=""
              className="relative z-20 inline-flex appearance-none bg-transparent py-1 pl-3 pr-8 text-sm font-medium outline-none"
            >
              <option value="" className="dark:bg-boxdark">
                Accidents
              </option>
              <option value="" className="dark:bg-boxdark">
                Deaths
              </option>
            </select>
          </h5>
        </div>
        <div>
          <div className="relative z-20 inline-block"></div>
        </div>
      </div>

      <div className="mb-2">
        <div id="chartThree" className="mx-auto flex justify-center">
          <ReactApexChart
            options={options}
            series={state.series}
            type="donut"
          />
        </div>
      </div>

      <div className="-mx-8 flex flex-wrap items-center justify-center gap-y-3">
        {carTypesData?.accidents_top.map((item: CarType) => (
          <div className="sm:w-1/2 w-full px-8">
            <div className="flex w-full items-center">
              <span className="mr-2 block h-3 w-full max-w-3 rounded-full bg-[#3C50E0]"></span>
              <p className="flex w-full justify-between text-sm font-medium text-black dark:text-white">
                <span> {item.marke} </span>
                <span> {item.total_accidents} </span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChartCarTypes;
