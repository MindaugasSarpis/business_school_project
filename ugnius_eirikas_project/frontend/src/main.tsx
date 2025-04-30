import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Map } from './pages/map/Map';
import './css/style.css';
import './css/satoshi.css';
import 'jsvectormap/dist/css/jsvectormap.css';
import 'flatpickr/dist/flatpickr.min.css';
import { HomePage } from './pages/HomePage';
import 'leaflet/dist/leaflet.css';
import { AnalysisPage } from './pages/analysis/AnalysisPage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const queryClient = new QueryClient();
const router = createBrowserRouter([
  { path: '/', element: <HomePage /> },
  { path: '/map', element: <Map /> },
  { path: '/analysis', element: <AnalysisPage /> },
]);
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>,
);
