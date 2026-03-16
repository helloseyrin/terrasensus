/**
 * Cost-Benefit Analysis types
 * Records fertiliser application events and ROI calculations.
 * Applications must be logged from day one — ROI analysis depends on historical data.
 */

export type FertiliserType =
  | "synthetic_nitrogen"
  | "synthetic_phosphorus"
  | "synthetic_potassium"
  | "npk_compound"
  | "organic_compost"
  | "slow_release_organic"
  | "biochar"
  | "cover_crop"            // not a product — marks a cover crop planting event
  | "mycorrhizal_inoculant"
  | "other";

export type EcoRating = "A" | "B" | "C" | "D" | "F";

export interface FertiliserApplication {
  id: string;
  plot_id: string;
  applied_at: string;              // ISO 8601
  fertiliser_type: FertiliserType;
  product_name: string;
  quantity_kg_per_ha: number;
  cost_per_ha: number;             // local currency
  currency: string;                // ISO 4217 e.g. "GBP", "EUR", "USD"
  was_flagged_unnecessary: boolean; // true if soil readings were within range at application time
  sensor_reading_at_application?: {
    nitrogen_mg_kg: number;
    phosphorus_mg_kg: number;
    potassium_mg_kg: number;
    ec_ds_m: number;
  };
  notes?: string;
}

export interface EcologicalImpact {
  fertiliser_type: FertiliserType;
  eco_rating: EcoRating;          // A = excellent, F = harmful
  nitrous_oxide_risk: "low" | "medium" | "high";   // GHG contribution
  runoff_risk: "low" | "medium" | "high";           // waterway contamination
  soil_invertebrate_impact: "positive" | "neutral" | "negative";
  biodiversity_note: string;      // plain language summary
}

export interface SeasonROIReport {
  plot_id: string;
  plot_name: string;
  season_start: string;           // ISO date
  season_end: string;             // ISO date
  total_applications: number;
  unnecessary_applications: number;
  total_fertiliser_spend: number;
  estimated_unnecessary_spend: number;
  estimated_savings_if_followed: number;
  savings_percentage: number;
  currency: string;
  soil_health_trend: "improving" | "stable" | "declining";
  ec_trend: "improving" | "stable" | "worsening";
  eco_score: EcoRating;
  eco_score_notes: string;
  regenerative_alternatives_suggested: string[];
}
