import styled from "@emotion/styled";
import { Icon, type IconName, Modal } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";

interface Props {
  visible: boolean;
  onClose: () => void;
}

const Step = ({
  number,
  title,
  description,
  icon,
}: {
  number: number;
  title: string;
  description: string;
  icon: IconName;
}) => {
  return (
    <StepContainer>
      <Icon name={icon} width={24} />
      <TextContainer>
        <Label content={`STEP ${number}`} color="gray40" />
        <Label size="Large" content={title} />
        <Body content={description} />
      </TextContainer>
    </StepContainer>
  );
};

export const ManualConnectionHowItWorksModal = ({
  visible,
  onClose,
}: Props) => {
  return (
    <Modal
      smKind="drawer"
      visible={visible}
      cancelHidden
      submitText="Got it"
      onClose={onClose}
      onCancel={onClose}
      onSubmit={onClose}
      title="How to manually create a new UMA connection"
    >
      <Steps>
        <Step
          number={1}
          title="Set permissions"
          description="Choose what the NWC-compatible third-party app or service can do with your UMA"
          icon="Checkmark"
        />
        <Step
          number={2}
          title="Connect your UMA"
          description="Finalize the connection by scanning or pasting the connection string into the app you want to connect"
          icon="QRCodeIcon"
        />
      </Steps>
    </Modal>
  );
};

const Steps = styled.section`
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: ${Spacing.xl};
`;

const StepContainer = styled.div`
  display: flex;
  flex-direction: row;
  gap: 24px;
  align-items: center;
`;

const TextContainer = styled.div`
  display: flex;
  flex-direction: column;
`;
