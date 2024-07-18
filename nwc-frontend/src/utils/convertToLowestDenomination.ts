import { type Currency } from "src/types/Currency";

export const convertToLowestDenomination = (
  amount: number,
  currency: Currency,
) => {
  return Math.round(amount * Math.pow(10, currency.decimals));
};
