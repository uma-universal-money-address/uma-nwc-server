import { Currency } from "./Currency";

export enum PermissionType {
  SEND_PAYMENTS = "SEND_PAYMENTS",
  READ_BALANCE = "READ_BALANCE",
  READ_TRANSACTIONS = "READ_TRANSACTIONS",
}

export interface Permission {
  type: PermissionType;
  description: string;
  optional?: boolean;
}

export interface PermissionState {
  permission: Permission;
  enabled: boolean;
}

export enum LimitFrequency {
  DAILY = "Daily",
  WEEKLY = "Weekly",
  MONTHLY = "Monthly",
}

export enum ExpirationPeriod {
  WEEK = "Week",
  MONTH = "Month",
  YEAR = "Year",
  NONE = "None",
}

export interface Connection {
  appId: string;
  name: string;
  domain: string;
  verified: boolean;
  createdAt: string;
  lastUsed: string;
  disconnectedAt: string;
  expiration: string;
  avatar: string;
  permissions: Permission[];
  amountInLowestDenom: number;
  amountInLowestDenomUsed: number;
  limitFrequency: LimitFrequency;
  limitEnabled: boolean;
  currency: Currency;
  isActive: boolean;
}
