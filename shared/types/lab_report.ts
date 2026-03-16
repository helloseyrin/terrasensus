export interface LabReport {
  id: string;
  plot_id: string;
  lab_name: string;
  report_ref: string;
  sample_date: string;       // ISO date
  sample_depth_cm: number;
  uploaded_at: string;       // ISO 8601
  gcs_uri: string;           // original file in Cloud Storage
  status: "pending" | "processing" | "complete" | "failed";
  results: LabResults | null;
}

export interface LabResults {
  ph: number;
  nitrogen_mg_kg: number;
  phosphorus_mg_kg: number;
  potassium_mg_kg: number;
  ec_ds_m: number;
  organic_matter_pct: number;
  cec_meq_100g: number;
  calcium_mg_kg: number;
  magnesium_mg_kg: number;
  zinc_mg_kg: number;
  iron_mg_kg: number;
  sand_pct: number;
  silt_pct: number;
  clay_pct: number;
}
