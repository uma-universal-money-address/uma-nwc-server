import { TextInput } from "@lightsparkdev/ui/components";
import { useState } from "react";
import { type Currency } from "src/types/Currency";
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

  const handleInputChange = (newValue: string) => {
    // Replace any non-decimal characters
    const amountInLowestDenom = newValue.replace(/[^0-9]/g, "");
    const amountAsNumber = parseInt(amountInLowestDenom, 10);
    setInputValue(
      formatAmountString({ currency, amountInLowestDenom: amountAsNumber }),
    );
    setAmount(amountAsNumber);
  };

  return (
    <TextInput
      inputMode="numeric"
      value={inputValue}
      onChange={handleInputChange}
    />
  );
};
