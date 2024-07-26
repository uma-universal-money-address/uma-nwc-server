import { Connection, LimitFrequency } from "src/types/Connection";

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
  return [
    {
      appId: "1",
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
      avatar: "/uma.svg",
      isActive: true,
    },
    {
      appId: "2",
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
      avatar: "/uma.svg",
      isActive: true,
    },
    {
      appId: "3",
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
      avatar: "/uma.svg",
      isActive: true,
    },
  ] as Connection[];
};
