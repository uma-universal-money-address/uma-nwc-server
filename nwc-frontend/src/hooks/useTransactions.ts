import { useEffect, useState } from "react";
import { type Currency } from "src/types/Currency";
import { getBackendUrl } from "src/utils/backendUrl";
import { fetchWithAuth } from "src/utils/fetchWithAuth";
import { formatTimestamp } from "src/utils/formatTimestamp";

export interface Transaction {
  id: string;
  budgetAmountInLowestDenom: number;
  sendingAmountInLowestDenom: number;
  createdAt: string;
}

interface RawTransaction {
  id: string;
  budget_currency: Currency;
  sending_currency: Currency;
  receiving_currency: Currency;
  budget_currency_amount: number;
  sending_currency_amount: number;
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
      budgetAmountInLowestDenom: rawTransaction.budget_currency_amount,
      sendingAmountInLowestDenom: rawTransaction.sending_currency_amount,
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
            throw new Error(
              `Failed to fetch transactions. connectionId: ${connectionId}`,
            );
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
