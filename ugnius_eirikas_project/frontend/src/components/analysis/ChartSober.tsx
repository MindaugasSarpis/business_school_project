import { useQuery } from '@tanstack/react-query';
import { ApexOptions } from 'apexcharts';
import React, { useEffect, useState } from 'react';
import ReactApexChart from 'react-apexcharts';
import { fetchStatsData } from '../../api/Api';
import Loader from '../../common/Loader';
import {
  CarTypesData,
  CarType,
  IntoxicatedDriver,
} from '../../interfaces/analysis/Interfaces';
import ChartCarTypes from './ChartCarTypes';

interface ChartSoberState {
  series: {
    name: string;
    data: number[];
  }[];
}

const ChartSober: React.FC = () => {
  const [state, setState] = useState<ChartSoberState>({
    series: [
      {
        name: 'Sober',
        data: [44],
      },
      {
        name: 'Intoxicated',
        data: [13],
      },
    ],
  });
  const {
    data: intoxicatedData,
    isLoading,
    isError,
  } = useQuery({
    queryFn: (): Promise<IntoxicatedDriver[]> =>
      fetchStatsData('http://127.0.0.1:8000/api/intoxicatedDrivers'),
    queryKey: ['intoxicatedDrivers', '2023'],
    staleTime: Infinity,
  });
  console.log(intoxicatedData);

  useEffect(() => {
    if (intoxicatedData && !isLoading && !isError) {
      setState({
        series: [
          {
            name: 'Sober',
            data: intoxicatedData.map(
              (item: IntoxicatedDriver) => item.sober_count,
            ),
          },
          {
            name: 'Intoxicated',
            data: intoxicatedData.map(
              (item: IntoxicatedDriver) => item.intoxicated_count,
            ),
          },
        ],
      });
    }
  }, [intoxicatedData]);
  if (isLoading)
    return (
      <div>
        <Loader />
      </div>
    );
  if (isError) return <div>Error</div>;
  const options: ApexOptions = {
    colors: ['#3C50E0', '#80CAEE'],
    chart: {
      fontFamily: 'Satoshi, sans-serif',
      type: 'bar',
      height: 335,
      stacked: true,
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
    },

    responsive: [
      {
        breakpoint: 1536,
        options: {
          plotOptions: {
            bar: {
              borderRadius: 0,
              columnWidth: '25%',
            },
          },
        },
      },
    ],
    plotOptions: {
      bar: {
        horizontal: false,
        borderRadius: 0,
        columnWidth: '25%',
        borderRadiusApplication: 'end',
        borderRadiusWhenStacked: 'last',
      },
    },
    dataLabels: {
      enabled: false,
    },

    xaxis: {
      categories: intoxicatedData?.map((item) => item.time),
    },
    legend: {
      position: 'top',
      horizontalAlign: 'left',
      fontFamily: 'Satoshi',
      fontWeight: 500,
      fontSize: '14px',

      markers: {
        radius: 99,
      },
    },
    fill: {
      opacity: 1,
    },
  };

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white p-7.5 shadow-default dark:border-strokedark dark:bg-boxdark xl:col-span-4">
      <div className="mb-4 justify-between gap-4 sm:flex">
        <div>
          <h4 className="text-xl font-semibold text-black dark:text-white">
            Intoxicated vs Sober
          </h4>
        </div>
      </div>
      <div>
        <div id="chartTwo" className="-ml-5 -mb-9">
          <ReactApexChart
            options={options}
            series={state.series}
            type="bar"
            height={350}
          />
        </div>
      </div>
    </div>
  );
};

export default ChartSober;
