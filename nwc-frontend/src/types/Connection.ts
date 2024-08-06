import { Currency } from "./Currency";

export enum PermissionType {
  SEND_PAYMENTS = "send_payments",
  READ_BALANCE = "read_balance",
  READ_TRANSACTIONS = "read_transactions",
}

export const PERMISSION_DESCRIPTIONS = {
  [PermissionType.SEND_PAYMENTS]: "Send payments from your UMA",
  [PermissionType.READ_BALANCE]: "Read your balance",
  [PermissionType.READ_TRANSACTIONS]: "Read transaction history",
};

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
  DAILY = "daily",
  WEEKLY = "weekly",
  MONTHLY = "monthly",
  NONE = "none",
}

export enum ExpirationPeriod {
  WEEK = "Week",
  MONTH = "Month",
  YEAR = "Year",
  NONE = "None",
}

export enum ConnectionStatus {
  ACTIVE = "Active",
  PENDING = "Pending",
  INACTIVE = "Inactive",
}

export interface InitialConnection {
  name: string;
  permissions: Permission[];
  currencyCode: string;
  amountInLowestDenom: number;
  limitEnabled: boolean;
  limitFrequency?: LimitFrequency;
  expiration?: string;
  clientId?: string;
}

export interface Connection {
  connectionId: string;
  clientId: string;
  name: string;
  createdAt: string;
  permissions: Permission[];
  amountInLowestDenom: number;
  amountInLowestDenomUsed: number;
  limitEnabled: boolean;
  currency: Currency;
  status: ConnectionStatus;
  limitFrequency?: LimitFrequency;
  expiration?: string;
  lastUsed?: string;
  disconnectedAt?: string;
}
