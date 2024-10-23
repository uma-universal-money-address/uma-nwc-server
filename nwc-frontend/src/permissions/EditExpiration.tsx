import styled from "@emotion/styled";
import { Button, Drawer, Icon } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Headline } from "@lightsparkdev/ui/components/typography/Headline";
import { useBreakpoints } from "@lightsparkdev/ui/styles/breakpoints";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { NwcModal } from "src/components/NwcModal";
import { ExpirationPeriod } from "src/types/Connection";
import { EnableToggle } from "./EnableToggle";
import { ExpirationPeriodPicker } from "./ExpirationPeriodPicker";

interface Props {
  visible: boolean;
  expirationPeriod: ExpirationPeriod;
  title: string;
  handleSubmit: ({
    expirationPeriod,
  }: {
    expirationPeriod: ExpirationPeriod;
  }) => void;
  handleCancel: () => void;
  isExistingConnection?: boolean;
}

export const EditExpiration = ({
  handleSubmit,
  handleCancel,
  visible,
  expirationPeriod,
  title,
  isExistingConnection,
}: Props) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(
    expirationPeriod !== ExpirationPeriod.NONE,
  );
  const [newExpirationPeriod, setNewExpirationPeriod] =
    useState<ExpirationPeriod>(expirationPeriod);
  const breakpoints = useBreakpoints();

  const handleChooseExpirationPeriod = (expirationPeriod: ExpirationPeriod) => {
    setNewExpirationPeriod(expirationPeriod);
    setIsEnabled(true);
  };

  const handleEnableToggle = (enabled: boolean) => {
    setIsEnabled(enabled);
    setNewExpirationPeriod(
      enabled ? ExpirationPeriod.YEAR : ExpirationPeriod.NONE,
    );
  };

  const contents = (
    <>
      <Intro>
        <Headline size="Small" content={title} />
        <Body
          size="Large"
          content="Protect your UMA by letting this connection expire automatically. You can always change this in settings."
        />
      </Intro>
      <Controls>
        <EnableToggle
          isEnabled={isEnabled}
          setIsEnabled={handleEnableToggle}
          title="Enable expiration date"
          id="expiration-toggle"
        />
        {isEnabled ? (
          <ExpirationPeriodPicker
            expirationPeriod={newExpirationPeriod}
            setExpirationPeriod={handleChooseExpirationPeriod}
          />
        ) : (
          <Warning>
            <Icon name="WarningSign" width={12} />
            <WarningText>
              Without an expiration date, this app will have access to your
              funds until you disconnect it manually.
            </WarningText>
          </Warning>
        )}
      </Controls>
    </>
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
            expirationPeriod: newExpirationPeriod,
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
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.xs};
`;

const Controls = styled.section`
  margin-bottom: 4px;
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const Warning = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.px.sm};
  align-items: center;
  padding: ${Spacing.px.md};
  border-radius: 8px;
  border: 1px solid ${colors.grayBlue80};
`;

const WarningText = styled.span`
  color: ${({ theme }) => theme.text};
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  letter-spacing: -0.175px;
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
