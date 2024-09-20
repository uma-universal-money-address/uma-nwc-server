import { useEffect, useState } from "react";

export interface Transaction {
  id: string;
  amountInLowestDenom: number;
  currencyCode: string;
  name: string;
  createdAt: string;
}

interface RawTransaction {
  id: string;
  amountInLowestDenom: number;
  currencyCode: string;
  createdAt: string;
}

const hydrateTransactions = (
  rawTransactions: RawTransaction[],
): Transaction[] => {
  return rawTransactions.map((rawTransaction) => {
    return {
      id: rawTransaction.id,
      amountInLowestDenom: rawTransaction.amountInLowestDenom,
      currencyCode: rawTransaction.currencyCode,
      createdAt: new Date(
        Date.parse(rawTransaction.createdAt),
      ).toLocaleString(),
    };
  });
};

export function useTransactions({ connectionId }: { connectionId: string }) {
  const [transactions, setTransactions] = useState<Transaction[]>();
  const [error, setError] = useState<string>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchTransactions(connectionId: string) {
      setIsLoading(true);
      try {
        // const response = await
        // fetchWithAuth(`${getBackendUrl()}/api/transactions/${connectionId}`, { method: "GET",
        // }).then((res) => { if (res.ok) { return res.json() as Promise<RawTransaction[]>; } else {
        // throw new Error("Failed to fetch transactions.", { connectionId }); } });
        const response = [
          {
            id: "1",
            amountInLowestDenom: 1000,
            currencyCode: "USD",
            createdAt: new Date().toISOString(),
          },
          {
            id: "2",
            amountInLowestDenom: 2000,
            currencyCode: "USD",
            createdAt: new Date().toISOString(),
          },
          {
            id: "3",
            amountInLowestDenom: 3000,
            currencyCode: "USD",
            createdAt: new Date().toISOString(),
          },
        ];

        if (!ignore) {
          setTransactions(hydrateTransactions(response));
          setIsLoading(false);
        }
      } catch (e: unknown) {
        const error = e as Error;
        setError(error.message);
        setIsLoading(false);
      }
    }

    let ignore = false;
    fetchTransactions(connectionId);
    return () => {
      ignore = true;
    };
  }, [connectionId]);

  return {
    transactions,
    error,
    isLoading,
  };
}
