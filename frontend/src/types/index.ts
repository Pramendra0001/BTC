export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface SystemStatus {
  status: 'OPERATIONAL' | 'DEGRADED' | 'ERROR' | 'UNAVAILABLE';
  services: Record<string, string>;
}
// Add other interfaces based on schemas to avoid empty typing
