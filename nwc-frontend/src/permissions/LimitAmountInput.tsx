import { TextInput } from "@lightsparkdev/ui/components";
import { useState } from "react";
import { Currency } from "src/types/Currency";
import { formatAmountString } from "src/utils/formatConnectionString";

interface Props {
  amount: number;
  setAmount: (amount: number) => void;
  currency: Currency;
}

export const LimitAmountInput = ({ amount, setAmount, currency }: Props) => {
  const [inputValue, setInputValue] = useState(
    formatAmountString({ currency, amountInLowestDenom: amount }),
  );
  const [amountInLowestDenom, setAmountInLowestDenom] = useState(amount);

  const handleInputChange = (newValue: string) => {
    // Replace any non-decimal characters
    const amountInLowestDenom = newValue.replace(/[^0-9]/g, "");
    setInputValue(formatAmountString({ currency, amountInLowestDenom }));
    setAmount(amountInLowestDenom);
  };

  return (
    <TextInput
      inputMode="numeric"
      value={inputValue}
      onChange={handleInputChange}
    />
  );
};
