interface Permission {
  type: string;
  description: string;
  optional?: boolean;
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
  amountPerMonthLowestDenom: number;
  currency: Currency;
  isActive: boolean;
}
