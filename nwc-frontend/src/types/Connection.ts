export interface Permission {
  type: string;
  description: string;
  optional?: boolean;
}

export enum LimitFrequency {
  DAILY = "Daily",
  WEEKLY = "Weekly",
  MONTHLY = "Monthly",
}

export interface Connection {
  appId: string;
  name: string;
  domain: string;
  verified: boolean;
  createdAt: string;
  lastUsed: string;
  avatar: string;
  permissions: Permission[];
  amountInLowestDenom: number;
  limitFrequency: LimitFrequency;
  limitEnabled: boolean;
  currency: Currency;
  isActive: boolean;
}
