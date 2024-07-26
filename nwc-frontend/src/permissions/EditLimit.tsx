import styled from "@emotion/styled";
import { Modal } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Currency } from "src/types/Currency";
import { EnableLimitToggle } from "./EnableLimitToggle";
import { LimitAmountInput } from "./LimitAmountInput";
import { LimitFrequencyPicker } from "./LimitFrequencyPicker";

interface Props {
  visible: boolean;
  amountInLowestDenom: number;
  currency: Currency;
  frequency: LimitFrequency;
  enabled: boolean;
  title: string;
  handleSubmit: ({
    frequency,
    enabled,
    amountInLowestDenom,
  }: {
    frequency: LimitFrequency;
    enabled: boolean;
    amountInLowestDenom: number;
  }) => void;
  handleCancel: () => void;
}

export const EditLimit = ({
  handleSubmit,
  handleCancel,
  visible,
  amountInLowestDenom,
  currency,
  frequency,
  enabled,
  title,
}: Props) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(enabled);
  const [newAmount, setNewAmount] = useState<number>(amountInLowestDenom);
  const [newFrequency, setNewFrequency] = useState<LimitFrequency>(frequency);

  return (
    <Modal
      smKind="drawer"
      cancelHidden
      submitText="Done"
      visible={visible}
      onSubmit={() =>
        handleSubmit({
          frequency: newFrequency,
          enabled: isEnabled,
          amountInLowestDenom: newAmount,
        })
      }
      onClose={handleCancel}
    >
      <Intro>
        <Title>{title}</Title>
        <Description>
          Protect your UMA by setting a spending limit. You can always change
          this in settings.
        </Description>
      </Intro>
      <Controls>
        <EnableLimitToggle isEnabled={isEnabled} setIsEnabled={setIsEnabled} />
        <LimitFrequencyPicker
          frequency={newFrequency}
          setFrequency={setNewFrequency}
        />
        <LimitAmountInput
          amount={newAmount}
          setAmount={setNewAmount}
          currency={currency}
        />
      </Controls>
    </Modal>
  );
};

const Title = styled.h1`
  color: ${({ theme }) => theme.text};
  font-size: 20px;
  font-style: normal;
  line-height: 28px;
  letter-spacing: -0.25px;
`;

const Description = styled.p`
  color: ${({ theme }) => theme.secondary};
  font-size: 14px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px;
  letter-spacing: -0.175px;
`;

const Intro = styled.section`
  margin-bottom: ${Spacing.xl};
`;

const Controls = styled.section`
  margin-bottom: ${Spacing.xl};
  display: flex;
  flex-direction: column;
  gap: ${Spacing.sm};
`;
