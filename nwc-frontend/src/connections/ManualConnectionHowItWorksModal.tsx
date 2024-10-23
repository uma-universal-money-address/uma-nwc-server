import styled from "@emotion/styled";
import { Button, Icon, type IconName } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Headline } from "@lightsparkdev/ui/components/typography/Headline";
import { Overline } from "@lightsparkdev/ui/components/typography/Overline";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { NwcModal } from "src/components/NwcModal";

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
        <Overline content={`STEP ${number}`} color="grayBlue43" />
        <Title content={title} />
        <Body size="Large" content={description} />
      </TextContainer>
    </StepContainer>
  );
};

export const ManualConnectionHowItWorksModal = ({
  visible,
  onClose,
}: Props) => {
  const buttons = (
    <Button text="Got it" kind="primary" onClick={onClose} paddingY="short" />
  );

  return (
    <NwcModal visible={visible} onClose={onClose} buttons={buttons} width={480}>
      <Steps>
        <Headline
          size="Small"
          content="How to manually create a new UMA connection"
        />
        <Step
          number={1}
          title="Set permissions"
          description="Choose what the NWC-compatible third-party app or service can do with your UMA"
          icon="Pencil"
        />
        <Step
          number={2}
          title="Connect your UMA"
          description="Finalize the connection by scanning or pasting the connection string into the app you want to connect"
          icon="QRCodeIcon"
        />
      </Steps>
    </NwcModal>
  );
};

const Steps = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px["xl"]};
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
