// Shared API types for Hifadhi.

export type SeasonStatus = "planned" | "active" | "harvested" | "failed";
export type LoanStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "disbursed"
  | "active"
  | "repaid"
  | "defaulted";
export type RiskLevel = "low" | "medium" | "high";
export type RecommendationPriority = "low" | "medium" | "high";

export interface Sacco {
  id: string;
  name: string;
  county: string | null;
  created_at: string;
}

export interface CreateSaccoBody {
  name: string;
  county?: string | null;
  admin_email: string;
  admin_password: string;
}

export interface Farmer {
  id: string;
  sacco_id: string;
  first_name: string;
  last_name: string;
  phone: string;
  national_id: string | null;
  created_at: string;
}

export interface CreateFarmerBody {
  sacco_id: string;
  first_name: string;
  last_name: string;
  phone: string;
  national_id?: string | null;
  login_email: string;
  login_password: string;
}

export interface Farm {
  id: string;
  farmer_id: string;
  name: string;
  county: string;
  acreage: string;
  latitude: number;
  longitude: number;
  created_at: string;
}

export interface CreateFarmBody {
  farmer_id: string;
  name: string;
  county: string;
  acreage: string;
  latitude: number;
  longitude: number;
}

export interface Season {
  id: string;
  farm_id: string;
  crop_type: string;
  planting_date: string;
  expected_harvest_date: string;
  status: SeasonStatus;
  created_at: string;
}

export interface CreateSeasonBody {
  farm_id: string;
  crop_type: string;
  planting_date: string;
  expected_harvest_date: string;
}

export interface Loan {
  id: string;
  farmer_id: string;
  amount: string;
  status: LoanStatus;
  risk_score: number | null;
  season_id?: string | null;
  created_at: string;
}

export interface CreateLoanBody {
  farmer_id: string;
  amount: string;
  season_id?: string | null;
}

export interface FarmerProfile {
  farmer: Farmer;
  farms: Farm[];
  loans: Loan[];
}

export interface RiskScore {
  loan_id: string;
  score: number;
  category: RiskLevel;
}

export interface RiskAssessment {
  id: string;
  loan_id: string;
  score: number;
  risk_level: RiskLevel;
  weather_risk?: number;
  season_risk?: number;
  harvest_risk?: number;
  financial_risk?: number;
  farmer_risk?: number;
  action?: string;
  created_at: string;
}

export interface RiskAssessmentResult {
  risk_assessment: RiskAssessment;
  analysis: {
    summary: string;
    explanation: string;
    recommendation: string;
    key_drivers: string[];
  };
}

export interface Recommendation {
  id: string;
  season_id: string;
  title: string;
  recommendation_text: string;
  priority: RecommendationPriority;
  created_at: string;
}
