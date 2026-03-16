/**
 * Activity Log + Quantity types — inspired by farmOS Log/Quantity pattern
 *
 * A farm is not just sensor readings. It is a collection of discrete events:
 * fertiliser applied, crop seeded, observation made, pest spotted, harvest recorded.
 * These are Logs. Each Log can contain Quantities (flexible value + unit measurements).
 *
 * This pattern is adopted from farmOS, which validated it across 150+ farms over 15 years.
 */

export type LogType =
  | "observation"            // general note / visual check
  | "lab_test"               // soil / water / plant tissue sample result
  | "seeding"                // crop planted
  | "harvest"                // crop harvested
  | "fertiliser_application" // fertiliser applied — feeds ROI calculation
  | "pesticide_application"  // pesticide/herbicide applied — feeds eco score
  | "maintenance"            // sensor or equipment maintenance
  | "movement"               // asset moved to a new location
  | "pest_observation"       // pest or disease spotted (optional image)
  | "irrigation";            // water applied

export type LogStatus = "done" | "pending";

export interface ActivityLog {
  id: string;
  plot_id: string;
  log_type: LogType;
  status: LogStatus;
  notes?: string;
  image_url?: string;         // for pest observations — stored in GCS
  logged_at: string;          // ISO 8601 — when the event HAPPENED (may differ from created_at)
  created_at: string;         // ISO 8601 — when the record was CREATED
  quantities: Quantity[];
}

export interface Quantity {
  id: string;
  log_id: string;
  label: string;              // e.g. "nitrogen", "yield", "applied_amount", "moisture_at_time"
  value: number;
  unit: string;               // mg/kg | % | t/ha | dS/m | pH | mm | kg/ha | L/ha | ...
}

// Crop lifecycle — planting to harvest
export interface CropCycle {
  id: string;
  plot_id: string;
  crop_type: string;
  variety?: string;
  planted_at?: string;         // ISO date
  expected_harvest_at?: string;
  harvested_at?: string;
  yield_t_ha?: number;
  notes?: string;
  created_at: string;
}

// Plot geometry — GeoJSON polygon for field boundary mapping
export interface PlotGeometry {
  plot_id: string;
  type: "Feature";
  geometry: {
    type: "Polygon" | "MultiPolygon" | "Point";
    coordinates: number[][][] | number[][];
  };
  properties: {
    name: string;
    area_ha: number;
    crop?: string;
  };
}
