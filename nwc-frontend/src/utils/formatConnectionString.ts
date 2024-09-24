import { LimitFrequency } from "src/types/Connection";
import { type Currency } from "src/types/Currency";
import { convertToNormalDenomination } from "./convertToNormalDenomination";

export const FREQUENCY_TO_SINGULAR_FORM: Record<LimitFrequency, string> = {
  [LimitFrequency.DAILY]: "day",
  [LimitFrequency.WEEKLY]: "week",
  [LimitFrequency.MONTHLY]: "month",
  [LimitFrequency.NONE]: "",
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
  const frequencyString =
    FREQUENCY_TO_SINGULAR_FORM[limitFrequency.toLowerCase() as LimitFrequency];
  const amountString = formatAmountString({ currency, amountInLowestDenom });
  return limitFrequency === LimitFrequency.NONE
    ? amountString
    : `${amountString}/${frequencyString}`;
};

export const formatAmountString = ({
  currency,
  amountInLowestDenom,
  decimals,
}: {
  currency: Currency;
  amountInLowestDenom: number;
  decimals?: number;
}) => {
  if (currency.symbol === "") {
    return `${convertToNormalDenomination(amountInLowestDenom, currency)} ${currency.code}`;
  }
  return `${currency.symbol}${convertToNormalDenomination(amountInLowestDenom, currency)}`;
};
