import styled from "@emotion/styled";
import { Modal } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";

interface Props {
  visible: boolean;
  vaspName: string;
  onClose: () => void;
}

export const LearnMoreModal = ({ visible, vaspName, onClose }: Props) => {
  return (
    <Modal
      smKind="drawer"
      visible={visible}
      cancelText="Close"
      onClose={onClose}
      onCancel={onClose}
      title={`How ${vaspName} connects your UMA securely to third-party apps and services`}
    >
      <Section>
        <Title content="How does it work?" size="Medium" />
        <Body
          color="grayBlue43"
          content={`You can unlock payments experiences on the apps and services you use by connecting your ${vaspName} UMA.`}
        />
        <Body
          color="grayBlue43"
          content={[
            "UMA connections are powered by ",
            {
              text: "Nostr Wallet Connect",
              externalLink: "https://nwc.dev/",
              color: "blue39",
            },
            ", a standardized protocol that enables apps and services to securely interact with other UMAs or wallets.",
          ]}
        />
      </Section>

      <Section>
        <Title content="You are in control" size="Medium" />
        <Body
          color="grayBlue43"
          content="For each app or service that you connect to your UMA, you can review permissions, edit your spending limit, view transactions, or disconnect your UMA."
        />
      </Section>
    </Modal>
  );
};

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xs};
  margin-top: ${Spacing["xl"]};
`;
