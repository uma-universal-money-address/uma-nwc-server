export interface Connection {
  appId: string;
  name: string;
  createdAt: string;
  lastUsed: string;
  avatar: string;
}

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
      avatar: "/uma.svg",
    },
    {
      appId: "2",
      name: "Test 2",
      createdAt: new Date().toISOString(),
      lastUsed: new Date().toISOString(),
      avatar: "/uma.svg",
    },
    {
      appId: "3",
      name: "Test 3",
      createdAt: new Date().toISOString(),
      lastUsed: new Date().toISOString(),
      avatar: "/uma.svg",
    },
  ] as Connection[];
};
