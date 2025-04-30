export interface StatsDetails {
  statistic: string;
  value: number;
}
export interface StatsData {
  data: StatsDetails[];
}
export interface LineChartsData {
  accidents: AccidentData[];
  deaths: DeathData[];
}
export interface AccidentData {
  date: string;
  total_accidents: number;
}
export interface DeathData {
  date: string;
  total_deaths: number;
}
interface accidentNoDeath {
  total_accidents: number;
  year_month: string;
}
interface accidentDeath {
  total_deaths: number;
  year_month: string;
}
export interface AccidentDataByMonth {
  accidents: accidentNoDeath[];
  deaths: accidentDeath[];
}
export interface DeathDataByMonth {
  total_deaths: number;
  year_month: string;
}

export interface CarTypesData {
  accidents: CarType[];
  accidents_top: CarType[];
  deaths: CarType[];
  deaths_top: CarType[];
}
export interface CarType {
  marke: string;
  total_accidents: number;
}

export interface IntoxicatedDriver {
  sober_count: number;
  intoxicated_count: number;
  time: string;
}
