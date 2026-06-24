import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from "@tanstack/react-query";
import api from "./api";
import type {
  CreateFarmBody,
  CreateFarmerBody,
  CreateLoanBody,
  CreateSaccoBody,
  CreateSeasonBody,
  Farm,
  Farmer,
  FarmerProfile,
  Loan,
  LoanStatus,
  Recommendation,
  RiskAssessment,
  RiskAssessmentResult,
  RiskScore,
  Sacco,
  Season,
  SeasonStatus,
} from "./types";

/* ---------- SACCOs ---------- */
export const saccoKeys = {
  all: ["saccos"] as const,
  list: (offset = 0, limit = 20) => ["saccos", "list", offset, limit] as const,
  detail: (id: string) => ["saccos", id] as const,
};

export interface SaccoListParams {
  offset?: number;
  limit?: number;
  search?: string;
  county?: string;
}
export function useSaccos(params: SaccoListParams = {}) {
  const { offset = 0, limit = 20, search, county } = params;
  return useQuery({
    queryKey: ["saccos", "list", { offset, limit, search, county }],
    queryFn: async () => {
      const { data } = await api.get<Sacco[]>("/saccos", {
        params: { offset, limit, search: search || undefined, county: county || undefined },
      });
      return data;
    },
  });
}


export function useSacco(id: string, opts?: Partial<UseQueryOptions<Sacco>>) {
  return useQuery({
    queryKey: saccoKeys.detail(id),
    queryFn: async () => (await api.get<Sacco>(`/saccos/${id}`)).data,
    ...opts,
  });
}

export function useCreateSacco() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: CreateSaccoBody) => (await api.post<Sacco>("/saccos", body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: saccoKeys.all }),
  });
}

/* ---------- Farmers ---------- */
export const farmerKeys = {
  all: ["farmers"] as const,
  profile: (id: string) => ["farmers", id, "profile"] as const,
};

export interface FarmerListParams {
  offset?: number;
  limit?: number;
  search?: string;
  sacco_id?: string;
}
export function useFarmers(params: FarmerListParams = {}) {
  const { offset = 0, limit = 20, search, sacco_id } = params;
  return useQuery({
    queryKey: ["farmers", "list", { offset, limit, search, sacco_id }],
    queryFn: async () =>
      (await api.get<Farmer[]>("/farmers", {
        params: { offset, limit, search: search || undefined, sacco_id: sacco_id || undefined },
      })).data,
  });
}


export function useFarmerProfile(id: string) {
  return useQuery({
    queryKey: farmerKeys.profile(id),
    queryFn: async () => (await api.get<FarmerProfile>(`/farmers/${id}`)).data,
  });
}

export function useCreateFarmer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: CreateFarmerBody) => (await api.post<Farmer>("/farmers", body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: farmerKeys.all }),
  });
}

/* ---------- Farms ---------- */
export const farmKeys = {
  all: ["farms"] as const,
  detail: (id: string) => ["farms", id] as const,
};

export function useFarm(id: string) {
  return useQuery({
    queryKey: farmKeys.detail(id),
    queryFn: async () => (await api.get<Farm>(`/farms/${id}`)).data,
  });
}

export function useCreateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: CreateFarmBody) => (await api.post<Farm>("/farms", body)).data,
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: farmKeys.all });
      qc.invalidateQueries({ queryKey: farmerKeys.profile(vars.farmer_id) });
    },
  });
}

/* ---------- Seasons ---------- */
export const seasonKeys = {
  all: ["seasons"] as const,
  detail: (id: string) => ["seasons", id] as const,
};

export interface SeasonListParams {
  offset?: number;
  limit?: number;
  search?: string;
  status?: SeasonStatus;
  crop_type?: string;
}
export function useSeasons(params: SeasonListParams = {}) {
  const { offset = 0, limit = 20, search, status, crop_type } = params;
  return useQuery({
    queryKey: ["seasons", "list", { offset, limit, search, status, crop_type }],
    queryFn: async () =>
      (await api.get<Season[]>("/seasons", {
        params: {
          offset,
          limit,
          search: search || undefined,
          status: status || undefined,
          crop_type: crop_type || undefined,
        },
      })).data,
  });
}


export function useSeason(id: string) {
  return useQuery({
    queryKey: seasonKeys.detail(id),
    queryFn: async () => (await api.get<Season>(`/seasons/${id}`)).data,
  });
}

export function useCreateSeason() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: CreateSeasonBody) => (await api.post<Season>("/seasons", body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: seasonKeys.all }),
  });
}

export function useSeasonTransition(id: string, action: Exclude<SeasonStatus, "planned">) {
  const qc = useQueryClient();
  const endpointMap: Record<typeof action, string> = {
    active: "activate",
    harvested: "harvest",
    failed: "fail",
  };
  return useMutation({
    mutationFn: async () =>
      (await api.patch<Season>(`/seasons/${id}/${endpointMap[action]}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: seasonKeys.detail(id) });
    },
  });
}

/* ---------- Loans ---------- */
export const loanKeys = {
  all: ["loans"] as const,
  detail: (id: string) => ["loans", id] as const,
  risk: (id: string, seasonId?: string | null) => ["loans", id, "risk", seasonId ?? null] as const,
};

export interface LoanListParams {
  offset?: number;
  limit?: number;
  search?: string;
  status?: LoanStatus;
  farmer_id?: string;
}
export function useLoans(params: LoanListParams = {}) {
  const { offset = 0, limit = 20, search, status, farmer_id } = params;
  return useQuery({
    queryKey: ["loans", "list", { offset, limit, search, status, farmer_id }],
    queryFn: async () =>
      (await api.get<Loan[]>("/loans", {
        params: {
          offset,
          limit,
          search: search || undefined,
          status: status || undefined,
          farmer_id: farmer_id || undefined,
        },
      })).data,
  });
}


export function useLoan(id: string) {
  return useQuery({
    queryKey: loanKeys.detail(id),
    queryFn: async () => (await api.get<Loan>(`/loans/${id}`)).data,
  });
}

export function useCreateLoan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (body: CreateLoanBody) => (await api.post<Loan>("/loans", body)).data,
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: loanKeys.all });
      qc.invalidateQueries({ queryKey: farmerKeys.profile(vars.farmer_id) });
    },
  });
}

export type LoanTransition =
  | "approve"
  | "reject"
  | "disburse"
  | "activate"
  | "repay"
  | "default";

export function useLoanTransition(id: string, action: LoanTransition) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await api.patch<Loan>(`/loans/${id}/${action}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: loanKeys.detail(id) }),
  });
}

export function transitionsForLoan(status: LoanStatus): {
  action: LoanTransition;
  label: string;
  variant: "default" | "destructive" | "success";
}[] {
  switch (status) {
    case "pending":
      return [
        { action: "approve", label: "Approve", variant: "default" },
        { action: "reject", label: "Reject", variant: "destructive" },
      ];
    case "approved":
      return [
        { action: "disburse", label: "Disburse", variant: "default" },
        { action: "reject", label: "Reject", variant: "destructive" },
      ];
    case "disbursed":
      return [{ action: "activate", label: "Activate", variant: "default" }];
    case "active":
      return [
        { action: "repay", label: "Mark repaid", variant: "success" },
        { action: "default", label: "Mark defaulted", variant: "destructive" },
      ];
    default:
      return [];
  }
}

/* ---------- Risk ---------- */
export function useLoanRiskScore(loanId: string, seasonId?: string | null) {
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.get<RiskScore>(`/loans/${loanId}/risk`, {
        params: seasonId ? { season_id: seasonId } : undefined,
      });
      return data;
    },
  });
}

/** Trigger a fresh risk recalculation — maps to POST /loans/{id}/risk/recalculate. */
export function useRunRiskAssessment(loanId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post<RiskScore>(
        `/loans/${loanId}/risk/recalculate`,
      );
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: loanKeys.detail(loanId) });
      qc.invalidateQueries({ queryKey: loanKeys.risk(loanId) });
    },
  });
}

/**
 * @deprecated The /risks-assessments endpoint does not exist on the backend.
 * These stubs keep callers from crashing while pages are updated to use
 * useLoanRiskScore / useRunRiskAssessment instead.
 */
export function useRiskAssessments(_offset = 0, _limit = 20) {
  return useQuery({
    queryKey: ["risk-assessments", "list"],
    queryFn: async (): Promise<RiskAssessment[]> => [],
    staleTime: Infinity,
  });
}

/** @deprecated See useRiskAssessments */
export function useRiskAssessment(_id: string) {
  return useQuery({
    queryKey: ["risk-assessments", _id],
    queryFn: async (): Promise<RiskAssessment | null> => null,
    staleTime: Infinity,
  });
}

/* ---------- Recommendations ---------- */
export function useSeasonRecommendations(seasonId: string) {
  return useQuery({
    queryKey: ["recommendations", "season", seasonId],
    queryFn: async () =>
      (await api.get<Recommendation[]>(`/recommendations/season/${seasonId}`)).data,
  });
}

export function useGenerateRecommendation(seasonId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post<{ recommendation: Recommendation }>(
        `/recommendations/generate/${seasonId}`,
      );
      return data.recommendation;
    },
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["recommendations", "season", seasonId] }),
  });
}

export function useRecentRecommendations(limit = 5) {
  return useQuery({
    queryKey: ["recommendations", "recent", limit],
    queryFn: async () => {
      try {
        const { data } = await api.get<Recommendation[]>("/recommendations", {
          params: { limit, offset: 0 },
        });
        return data;
      } catch {
        return [] as Recommendation[];
      }
    },
  });
}
