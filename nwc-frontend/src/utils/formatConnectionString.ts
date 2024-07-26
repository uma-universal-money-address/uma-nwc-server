import { LimitFrequency } from "src/types/Connection";
import { Currency } from "src/types/Currency";
import { convertToNormalDenomination } from "./convertToNormalDenomination";

export const FREQUENCY_TO_SINGULAR_FORM: Record<LimitFrequency, string> = {
  [LimitFrequency.DAILY]: "day",
  [LimitFrequency.WEEKLY]: "week",
  [LimitFrequency.MONTHLY]: "month",
};

export const formatConnectionString = ({
  currency,
  limitFrequency,
  amountInLowestDenom,
}: {
  currency: Currency;
  limitFrequency: LimitFrequency;
  amountInLowestDenom: number;
}) => {
  const frequencyString = FREQUENCY_TO_SINGULAR_FORM[limitFrequency];
  const amountString = formatAmountString({ currency, amountInLowestDenom });
  return `${amountString}/${frequencyString}`;
};

export const formatAmountString = ({
  currency,
  amountInLowestDenom,
}: {
  currency: Currency;
  amountInLowestDenom: number;
}) => {
  return `${currency.symbol}${convertToNormalDenomination(amountInLowestDenom, currency)}`;
};
