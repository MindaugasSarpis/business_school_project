import axios from 'axios';

export const fetchStatsData = async (endpoint: string): Promise<any> => {
  try {
    const res = await axios.get(endpoint);
    return res.data;
  } catch (error) {
    console.error(error);
  }
};

export const fetchLineCharts = async (endpoint: string): Promise<any> => {
  try {
    const res = await axios.get(endpoint);
    return res.data;
  } catch (error) {
    console.error(error);
  }
};
