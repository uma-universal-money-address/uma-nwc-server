import { useEffect, useState } from "react";
import { Currency } from "src/types/Currency";

interface UserCurrenciesResponse {
  defaultCurrency: Currency;
  currencies: Currency[];
}

export const useUserCurrencies = () => {
  const [defaultCurrency, setDefaultCurrency] = useState<Currency>();
  const [currencies, setCurrencies] = useState<Currency[]>();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchUserCurrencies() {
      setIsLoading(true);
      try {
        // const response = await fetch(
        //   "/user/currencies",
        //   {
        //     method: "GET",
        //   },
        // ).then((res) => {
        //   if (res.ok) {
        //     return res.json() as Promise<UserCurrenciesResponse>;
        //   } else {
        //     throw new Error("Failed to fetch exchange rates.");
        //   }
        // });
        const response = {
          defaultCurrency: {
            code: "USD",
            name: "United States Dollar",
            symbol: "$",
            decimals: 2,
            type: "fiat",
          },
          currencies: [
            {
              code: "USD",
              name: "United States Dollar",
              symbol: "$",
              decimals: 2,
              type: "fiat",
            },
            {
              code: "EUR",
              name: "Euro",
              symbol: "€",
              decimals: 2,
              type: "fiat",
            },
            {
              code: "JPY",
              name: "Japanese Yen",
              symbol: "¥",
              decimals: 0,
              type: "fiat",
            },
          ],
        };
        if (!ignore) {
          setDefaultCurrency(response.defaultCurrency);
          setCurrencies(response.currencies);
          setIsLoading(false);
        }
      } catch (e: unknown) {
        const error = e as Error;
        setError(error.message);
        setIsLoading(false);
      }
    }

    let ignore = false;
    fetchUserCurrencies();
    return () => {
      ignore = true;
    };
  }, []);

  return {
    defaultCurrency,
    error,
    isLoading,
  };
};
