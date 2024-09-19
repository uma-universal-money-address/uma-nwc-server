import dayjs from "dayjs";
import {
  Connection,
  ConnectionStatus,
  LimitFrequency,
  PERMISSION_DESCRIPTIONS,
  PermissionType,
} from "src/types/Connection";
import { getBackendUrl } from "./backendUrl";
import { fetchWithAuth } from "./fetchWithAuth";

export const MOCKED_CONNECTIONS: Connection[] = [
  {
    connectionId: "1",
    clientId: "1",
    name: "Test",
    createdAt: new Date().toISOString(),
    lastUsed: new Date().toISOString(),
    amountInLowestDenom: 300,
    amountInLowestDenomUsed: 200,
    limitFrequency: LimitFrequency.MONTHLY,
    limitEnabled: true,
    currency: {
      code: "USD",
      name: "US Dollar",
      symbol: "$",
      decimals: 2,
      type: "fiat",
    },
    permissions: [
      {
        type: PermissionType.SEND_PAYMENTS,
        description: "Send payments from your UMA",
      },
      {
        type: PermissionType.RECEIVE_PAYMENTS,
        description: "Receive payments to your UMA",
        optional: true,
      },
      {
        type: PermissionType.READ_BALANCE,
        description: "Read your balance",
        optional: true,
      },
      {
        type: PermissionType.READ_TRANSACTIONS,
        description: "Read transaction history",
        optional: true,
      },
    ],
    avatar: "/uma.svg",
    status: ConnectionStatus.ACTIVE,
  },
  {
    connectionId: "2",
    clientId: "2",
    name: "Test 2",
    createdAt: new Date().toISOString(),
    lastUsed: new Date().toISOString(),
    amountInLowestDenom: 100,
    amountInLowestDenomUsed: 10,
    limitFrequency: LimitFrequency.DAILY,
    limitEnabled: true,
    currency: {
      code: "USD",
      name: "US Dollar",
      symbol: "$",
      decimals: 2,
      type: "fiat",
    },
    permissions: [
      {
        type: PermissionType.SEND_PAYMENTS,
        description: "Send payments from your UMA",
      },
      {
        type: PermissionType.RECEIVE_PAYMENTS,
        description: "Receive payments to your UMA",
        optional: true,
      },
      {
        type: PermissionType.READ_BALANCE,
        description: "Read your balance",
        optional: true,
      },
      {
        type: PermissionType.READ_TRANSACTIONS,
        description: "Read transaction history",
        optional: true,
      },
    ],
    avatar: "/uma.svg",
    status: ConnectionStatus.ACTIVE,
  },
  {
    connectionId: "3",
    clientId: "3",
    name: "Test 3",
    createdAt: new Date().toISOString(),
    lastUsed: new Date().toISOString(),
    amountInLowestDenom: 200,
    amountInLowestDenomUsed: 70,
    limitFrequency: LimitFrequency.WEEKLY,
    limitEnabled: true,
    currency: {
      code: "USD",
      name: "US Dollar",
      symbol: "$",
      decimals: 2,
      type: "fiat",
    },
    permissions: [
      {
        type: PermissionType.SEND_PAYMENTS,
        description: "Send payments from your UMA",
      },
      {
        type: PermissionType.RECEIVE_PAYMENTS,
        description: "Receive payments to your UMA",
        optional: true,
      },
      {
        type: PermissionType.READ_BALANCE,
        description: "Read your balance",
        optional: true,
      },
      {
        type: PermissionType.READ_TRANSACTIONS,
        description: "Read transaction history",
        optional: true,
      },
    ],
    avatar: "/uma.svg",
    status: ConnectionStatus.INACTIVE,
  },
  {
    connectionId: "4",
    clientId: "4",
    name: "Test 4",
    createdAt: new Date().toISOString(),
    amountInLowestDenom: 200,
    amountInLowestDenomUsed: 0,
    limitFrequency: LimitFrequency.WEEKLY,
    limitEnabled: true,
    currency: {
      code: "USD",
      name: "US Dollar",
      symbol: "$",
      decimals: 2,
      type: "fiat",
    },
    permissions: [
      {
        type: PermissionType.SEND_PAYMENTS,
        description: "Send payments from your UMA",
      },
      {
        type: PermissionType.RECEIVE_PAYMENTS,
        description: "Receive payments to your UMA",
        optional: true,
      },
      {
        type: PermissionType.READ_BALANCE,
        description: "Read your balance",
        optional: true,
      },
      {
        type: PermissionType.READ_TRANSACTIONS,
        description: "Read transaction history",
        optional: true,
      },
    ],
    status: ConnectionStatus.PENDING,
  },
];

interface RawConnection {
  connection_id: string;
  client_app: {
    client_id: string;
    avatar: string;
  };
  name: string;
  created_at: number;
  last_used: number;
  amount_in_lowest_denom: number;
  amount_in_lowest_denom_used: number;
  limit_frequency: LimitFrequency;
  limit_enabled: boolean;
  currency: {
    code: string;
    symbol: string;
    decimals: number;
  };
  permissions: {
    type: PermissionType;
    description: string;
    optional?: boolean;
  }[];
  expires_at?: number;
  status: ConnectionStatus;
}

const mapPermissions = (permissions: RawConnection["permissions"]) => {
  return permissions.map((permission) => ({
    type: permission.type,
    description: PERMISSION_DESCRIPTIONS[permission.type],
  }));
};

const getStatus = (rawConnection: RawConnection): ConnectionStatus => {
  if (!rawConnection.expires_at) return ConnectionStatus.ACTIVE;
  return dayjs(rawConnection.expires_at).isAfter(dayjs())
    ? ConnectionStatus.ACTIVE
    : ConnectionStatus.INACTIVE;
};

export const fetchConnections = async () => {
  const rawConnections = await fetchWithAuth(
    `${getBackendUrl()}/api/connections`,
    {
      method: "GET",
    },
  ).then((res) => {
    if (res.ok) {
      return res.json() as Promise<RawConnection[]>;
    } else {
      throw new Error("Failed to fetch connections.");
    }
  });

  return rawConnections.map((rawConnection) => ({
    connectionId: rawConnection.connection_id,
    clientId: rawConnection.client_app.client_id,
    name: rawConnection.name,
    createdAt: rawConnection.created_at,
    lastUsed: rawConnection.last_used,
    amountInLowestDenom: rawConnection.amount_in_lowest_denom,
    amountInLowestDenomUsed: rawConnection.amount_in_lowest_denom_used,
    limitFrequency: rawConnection.limit_frequency,
    limitEnabled: rawConnection.limit_enabled,
    currency: {
      code: rawConnection.currency.code,
      symbol: rawConnection.currency.symbol,
      decimals: rawConnection.currency.decimals,
    },
    permissions: mapPermissions(rawConnection.permissions),
    avatar: rawConnection.client_app.avatar,
    status: getStatus(rawConnection),
  }));
};
