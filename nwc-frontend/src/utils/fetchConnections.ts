import {
  Connection,
  ConnectionStatus,
  LimitFrequency,
  PermissionType,
} from "src/types/Connection";

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

// eslint-disable-next-line @typescript-eslint/require-await
export const fetchConnections = async () => {
  // return fetch(`${getBackendUrl()}/connections`, {
  //   method: "GET",
  // }).then((res) => {
  //   if (res.ok) {
  //     return res.json() as Promise<Connection[]>;
  //   } else {
  //     throw new Error("Failed to fetch connections.");
  //   }
  // });
  return MOCKED_CONNECTIONS;
};
