import styled from "@emotion/styled";
import { TextInput } from "@lightsparkdev/ui/components";
import { useState } from "react";
import { type LimitFrequency } from "src/types/Connection";
import { type Currency } from "src/types/Currency";
import { formatAmountString } from "src/utils/formatConnectionString";

interface Props {
  amount: number;
  setAmount: (amount: number) => void;
  currency: Currency;
  frequency: LimitFrequency;
}

export const LimitAmountInput = ({
  amount,
  setAmount,
  currency,
  frequency,
}: Props) => {
  const [inputValue, setInputValue] = useState(
    formatAmountString({ currency, amountInLowestDenom: amount }),
  );

  const handleInputChange = (newValue: string) => {
    // Replace any non-decimal characters
    const amountInLowestDenom = newValue.replace(/[^0-9]/g, "");
    const amountAsNumber = parseInt(amountInLowestDenom || "0", 10);
    setInputValue(
      formatAmountString({ currency, amountInLowestDenom: amountAsNumber }),
    );
    setAmount(amountAsNumber);
  };

  return (
    <InputContainer>
      <TextInput
        typography={{
          type: "Body",
          size: "Large",
        }}
        inputMode="numeric"
        value={inputValue}
        onChange={handleInputChange}
      />
      {frequency !== "none" && (
        <SpendingLimitText>{`${frequency} spending limit`}</SpendingLimitText>
      )}
    </InputContainer>
  );
};

const InputContainer = styled.div`
  position: relative;
`;

const SpendingLimitText = styled.div`
  position: absolute;
  right: 16px;
  top: 13px;
  z-index: 2;
  font-size: 16px;
  font-weight: 500;
  line-height: 24px; /* 150% */
  color: #686a72;
`;
