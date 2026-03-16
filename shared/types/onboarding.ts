/**
 * Plot onboarding types — LLM-generated soil education at plot registration.
 * The onboarding call is the first time Gemini is invoked for a farmer.
 * Response is cached on the plot record and displayed during first-time setup.
 */

export interface PlotRegistration {
  farmer_name: string;
  region: string;
  crop: string;
  variety: string;
  area_ha: number;
  climate_zone: "continental" | "arid" | "maritime" | "tropical" | "mediterranean" | "other";
  farming_style: "conventional" | "regenerative" | "organic" | "mixed";
  // Initial sensor readings or estimates — can be null if sensors not yet installed
  moisture?: number;
  temperature?: number;
  ph?: number;
  nitrogen?: number;
  phosphorus?: number;
  potassium?: number;
  ec?: number;
  // Location
  latitude: number;
  longitude: number;
  geometry?: object;   // GeoJSON polygon — optional at registration, add later via map
}

export interface WatchListItem {
  sensor: string;
  why_it_matters: string;
  what_to_watch_for: string;
  plain_english_range: string;   // e.g. "For Pinot Noir, pH 5.5–6.8 — slightly acidic"
}

export interface OnboardingResponse {
  plot_id: string;
  welcome_message: string;
  soil_portrait: string;
  current_reading_interpretation: string;
  watch_list: WatchListItem[];
  regional_risk: string;
  one_thing_to_learn: string;
  regenerative_note: string;
  crop_thresholds: Record<string, {
    critical_low: number;
    low: number;
    high: number;
    critical_high: number;
    unit: string;
  }>;
}
