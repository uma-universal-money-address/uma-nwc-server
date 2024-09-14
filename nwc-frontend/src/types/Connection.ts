import { Currency } from "./Currency";

export enum PermissionType {
  SEND_PAYMENTS = "send_payments",
  READ_BALANCE = "read_balance",
  READ_TRANSACTIONS = "read_transactions",
  RECEIVE_PAYMENTS = "receive_payments",
}

export const PERMISSION_DESCRIPTIONS = {
  [PermissionType.SEND_PAYMENTS]: "Send payments from your UMA",
  [PermissionType.READ_BALANCE]: "Read your balance",
  [PermissionType.READ_TRANSACTIONS]: "Read transaction history",
  [PermissionType.RECEIVE_PAYMENTS]: "Receive payments",
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
  permissions: PermissionType[];
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

export const DEFAULT_CONNECTION_SETTINGS: ConnectionSettings = {
  permissionStates: [
    {
      permission: {
        type: PermissionType.SEND_PAYMENTS,
        description: "Send payments from your UMA",
      },
      enabled: true,
    },
    {
      permission: {
        type: PermissionType.RECEIVE_PAYMENTS,
        description: "Receive payments to your UMA",
        optional: true,
      },
      enabled: false,
    },
    {
      permission: {
        type: PermissionType.READ_BALANCE,
        description: "Read your balance",
        optional: true,
      },
      enabled: false,
    },
    {
      permission: {
        type: PermissionType.READ_TRANSACTIONS,
        description: "Read transaction history",
        optional: true,
      },
      enabled: false,
    },
  ],
  amountInLowestDenom: 50000,
  limitFrequency: LimitFrequency.NONE,
  limitEnabled: true,
  expirationPeriod: ExpirationPeriod.YEAR,
};
