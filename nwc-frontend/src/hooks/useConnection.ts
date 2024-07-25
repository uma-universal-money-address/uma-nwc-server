import { useEffect, useState } from "react";
import { Connection, LimitFrequency } from "src/types/Connection";

export const useConnection = ({ appId }: { appId: string }) => {
  const [connection, setConnection] = useState<Connection>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchConnection() {
      try {
        // const response = await fetch("/connection");
        // const connection = await response.json();
        setIsLoading(true);
        const connection = {
          appId: "1",
          name: "Cool App",
          domain: "coolapp.com",
          verified: true,
          createdAt: new Date().toISOString(),
          lastUsed: new Date().toISOString(),
          avatar: "/uma.svg",
          permissions: [
            {
              type: "READ_BALANCE",
              description: "Read your balance",
            },
            {
              type: "READ_TRANSACTIONS",
              description: "Read transaction history",
            },
            {
              type: "SEND_PAYMENTS",
              description: "Send payments from your UMA",
            },
          ],
          amountInLowestDenom: 200,
          amountInLowestDenomUsed: 40,
          limitFrequency: LimitFrequency.MONTHLY,
          limitEnabled: true,
          currency: {
            code: "USD",
            name: "US Dollar",
            symbol: "$",
            decimals: 2,
            type: "fiat",
          },
          isActive: true,
        } as Connection;
        setConnection(connection);
      } catch (e) {
        console.error(e);
      }

      setIsLoading(false);
    }

    let ignore = false;
    fetchConnection();
    return () => {
      ignore = true;
    };
  }, [appId]);

  // eslint-disable-next-line @typescript-eslint/require-await
  const updateConnection = async ({
    amountInLowestDenom,
    limitFrequency,
    limitEnabled,
    isActive,
  }: {
    amountInLowestDenom: number;
    limitFrequency: LimitFrequency;
    limitEnabled: boolean;
    isActive: boolean;
  }) => {
    try {
      // const response = await fetch("/connection", {
      //   method: "POST",
      //   body: JSON.stringify({ appId: connection.appId, amountInLowestDenom, limitFrequency, limitEnabled, isActive }),
      // });
      setConnection({
        ...connection,
        amountInLowestDenom,
        limitFrequency,
        limitEnabled,
        isActive,
        disconnectedAt: isActive ? undefined : new Date().toISOString(),
      });
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  };

  return {
    connection,
    isLoading,
    updateConnection,
  };
};
