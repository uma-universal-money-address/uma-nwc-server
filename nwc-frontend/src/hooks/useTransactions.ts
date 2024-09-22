import { useEffect, useState } from "react";
import { getBackendUrl } from "src/utils/backendUrl";
import { fetchWithAuth } from "src/utils/fetchWithAuth";
import { formatTimestamp } from "src/utils/formatTimestamp";

export interface Transaction {
  id: string;
  amountInLowestDenom: number;
  currencyCode: string;
  createdAt: string;
}

interface RawTransaction {
  id: string;
  budget_currency_amount: number;
  budget_currency_code: string;
  sending_currency_amount: number;
  sending_currency_code: string;
  receiver: string;
  receiver_type: string;
  status: string;
  created_at: string;
}

const hydrateTransactions = (
  rawTransactions: RawTransaction[],
): Transaction[] => {
  return rawTransactions.map((rawTransaction) => {
    return {
      id: rawTransaction.id,
      amountInLowestDenom: rawTransaction.sending_currency_amount,
      currencyCode: rawTransaction.sending_currency_code,
      createdAt: formatTimestamp(rawTransaction.created_at),
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
        const response = await fetchWithAuth(
          `${getBackendUrl()}/api/connection/${connectionId}/transactions?limit=20`,
          { method: "GET" },
        ).then((res) => {
          if (res.ok) {
            return res.json() as Promise<{
              count: number;
              transactions: RawTransaction[];
            }>;
          } else {
            throw new Error("Failed to fetch transactions.", { connectionId });
          }
        });

        if (!ignore) {
          setTransactions(hydrateTransactions(response.transactions));
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
