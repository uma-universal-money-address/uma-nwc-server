import { useEffect, useState } from "react";
import { Connection } from "src/types/Connection";
import { Currency } from "src/types/Currency";

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
          amountPerMonthLowestDenom: 200,
          currency: {
            symbol: "$",
            name: "US Dollar",
            decimals: 2,
          } as Currency,
          isActive: false,
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
  const updateConnection = async ({ amountPerMonthLowestDenom }: { amountPerMonthLowestDenom: number }) => {
    try {
      // await fetch("/connection", {
      //   method: "POST",
      //   body: JSON.stringify({ appId: connection.appId, amountPerMonthLowestDenom }),
      // });
      setConnection({
        ...connection,
        amountPerMonthLowestDenom,
      });
    } catch (e) {
      console.error(e);
    }
  };

  return {
    connection,
    isLoading,
    updateConnection,
  };
};