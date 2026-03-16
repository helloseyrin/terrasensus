export interface SensorReading {
  plot_id: string;
  plot_name: string;
  latitude: number;
  longitude: number;
  crop: string;
  timestamp: string; // ISO 8601
  sensors: {
    moisture: number;       // %
    temperature: number;    // °C
    ph: number;
    nitrogen: number;       // mg/kg
    phosphorus: number;     // mg/kg
    potassium: number;      // mg/kg
    ec: number;             // dS/m
  };
}

export type SensorName = keyof SensorReading["sensors"];

export interface SensorThreshold {
  sensor: SensorName;
  critical_low: number;
  low: number;
  high: number;
  critical_high: number;
  unit: string;
}
