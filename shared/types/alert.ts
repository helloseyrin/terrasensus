export type AlertLevel = "warning" | "critical";
export type AlertDirection = "low" | "high";
export type AlertSource = "sensor" | "drought" | "lab_report";

export interface Alert {
  id: string;
  plot_id: string;
  plot_name: string;
  source: AlertSource;
  sensor?: string;
  level: AlertLevel;
  direction?: AlertDirection;
  value?: number;
  unit?: string;
  message: string;
  recommendation?: string;
  created_at: string;        // ISO 8601
  acknowledged: boolean;
}

export interface DroughtAlert extends Alert {
  source: "drought";
  risk_score: number;        // 0.0–1.0
  rainfall_30d_mm: number;
  moisture_7d_delta: number;
}
