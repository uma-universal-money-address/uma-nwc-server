import { json, LoaderFunction } from "react-router-dom";

export interface UserCurrenciesResponse {
  defaultCurrency: Currency;
  currencies: Currency[];
}

export const userCurrencies = (async () => {
  // return await fetch(
  //   "/user/currencies",
  //   {
  //     method: "GET",
  //   },
  // );
  return json(
    {
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
    } as UserCurrenciesResponse,
    { status: 200 },
  );
}) satisfies LoaderFunction;
