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

export interface InitialConnection {
  name: string;
  permissions: Permission[];
  currencyCode: string;
  amountInLowestDenom: number;
  limitEnabled: boolean;
  limitFrequency?: LimitFrequency;
  expiration?: string;
  appId?: string;
}

export interface Connection {
  appId: string;
  name: string;
  verified: boolean;
  createdAt: string;
  permissions: Permission[];
  amountInLowestDenom: number;
  amountInLowestDenomUsed: number;
  limitEnabled: boolean;
  currency: Currency;
  isActive: boolean;
  domain?: string;
  limitFrequency?: LimitFrequency;
  expiration?: string;
  avatar?: string;
  lastUsed?: string;
  disconnectedAt?: string;
}
