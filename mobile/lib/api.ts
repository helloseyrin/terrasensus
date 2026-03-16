/**
 * TerraSensus API client — shared between mobile and web.
 * Base URL is set via environment variable.
 */
import type { Alert } from "../../shared/types/alert";
import type { LabReport } from "../../shared/types/lab_report";
import type { SensorReading } from "../../shared/types/sensor";

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8001";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  sensor: {
    latestByPlot: (plotId: string) =>
      get<SensorReading>(`/plots/${plotId}/readings/latest`),
    history: (plotId: string, hours = 24) =>
      get<SensorReading[]>(`/plots/${plotId}/readings?hours=${hours}`),
  },
  alerts: {
    list: (plotId?: string) =>
      get<Alert[]>(plotId ? `/alerts?plot_id=${plotId}` : "/alerts"),
  },
  labReports: {
    list: (plotId?: string) =>
      get<LabReport[]>(plotId ? `/lab-reports?plot_id=${plotId}` : "/lab-reports"),
    upload: async (plotId: string, file: FormData) => {
      const res = await fetch(`${BASE_URL}/lab-reports`, {
        method: "POST",
        body: file,
      });
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      return res.json() as Promise<LabReport>;
    },
  },
  recommendations: {
    get: (plotId: string) =>
      get<{ soil: string; suppliers: unknown[]; crop: string }>(`/recommendations/${plotId}`),
  },
};
