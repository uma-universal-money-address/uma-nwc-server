import styled from "@emotion/styled";
import { Icon, Modal } from "@lightsparkdev/ui/components";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
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
}

export const EditExpiration = ({
  handleSubmit,
  handleCancel,
  visible,
  expirationPeriod,
  title,
}: Props) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(
    expirationPeriod !== ExpirationPeriod.NONE,
  );
  const [newExpirationPeriod, setNewExpirationPeriod] =
    useState<ExpirationPeriod>(expirationPeriod);

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

  return (
    <Modal
      smKind="drawer"
      cancelHidden
      submitText="Done"
      visible={visible}
      onSubmit={() =>
        handleSubmit({
          expirationPeriod: newExpirationPeriod,
        })
      }
      onClose={handleCancel}
    >
      <Intro>
        <Title>{title}</Title>
        <Description>
          Protect your UMA by letting this connection expire automatically. You
          can always change this in settings.
        </Description>
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

const Warning = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.sm};
  align-items: center;
  padding: ${Spacing.md};
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
