import styled from "@emotion/styled";
import { Button, Drawer } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Headline } from "@lightsparkdev/ui/components/typography/Headline";
import { useBreakpoints } from "@lightsparkdev/ui/styles/breakpoints";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { NwcModal } from "src/components/NwcModal";
import { type LimitFrequency } from "src/types/Connection";
import { type Currency } from "src/types/Currency";
import { EnableToggle } from "./EnableToggle";
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
  isExistingConnection?: boolean;
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
  isExistingConnection,
}: Props) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(enabled);
  const [newAmount, setNewAmount] = useState<number>(amountInLowestDenom);
  const [newFrequency, setNewFrequency] = useState<LimitFrequency>(frequency);
  const breakpoints = useBreakpoints();

  const contents = (
    <Contents>
      <Intro>
        <Headline size="Small" content={title} />
        <Body
          size="Large"
          content="Protect your UMA by setting a spending limit. You can always change this in settings."
        />
      </Intro>
      <Controls>
        <EnableToggle
          isEnabled={isEnabled}
          setIsEnabled={setIsEnabled}
          title="Enable spending limit"
          id="enable-limit"
        />
        <LimitFrequencyPicker
          frequency={newFrequency}
          setFrequency={setNewFrequency}
        />
        <LimitAmountInput
          amount={newAmount}
          setAmount={setNewAmount}
          currency={currency}
          frequency={newFrequency}
        />
      </Controls>
    </Contents>
  );

  const buttons = (
    <ButtonContainer>
      {isExistingConnection && (
        <Button
          text="Cancel"
          kind="quaternary"
          paddingY="short"
          fullWidth={breakpoints.isSm()}
          onClick={handleCancel}
        />
      )}
      <Button
        text={isExistingConnection ? "Save changes" : "Done"}
        kind={isExistingConnection ? "primary" : "tertiary"}
        fullWidth={breakpoints.isSm()}
        paddingY="short"
        onClick={() =>
          handleSubmit({
            frequency: newFrequency,
            enabled: isEnabled,
            amountInLowestDenom: newAmount,
          })
        }
      />
    </ButtonContainer>
  );

  return breakpoints.isSm() ? (
    visible && (
      <Drawer padding="24px" kind="floating" onClose={handleCancel} closeButton>
        <DrawerContents>{contents}</DrawerContents>
        {buttons}
      </Drawer>
    )
  ) : (
    <NwcModal visible={visible} onClose={handleCancel} buttons={buttons}>
      {contents}
    </NwcModal>
  );
};

const Intro = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.xs};
`;

const Controls = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const Contents = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.lg};
`;

const DrawerContents = styled.div`
  padding-bottom: 24px;
  padding-top: 28px;
`;

const ButtonContainer = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.px.xs};
`;
