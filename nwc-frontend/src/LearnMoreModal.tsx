import styled from "@emotion/styled";
import { Button } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Headline } from "@lightsparkdev/ui/components/typography/Headline";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { NwcModal } from "./components/NwcModal";

interface Props {
  visible: boolean;
  vaspName: string;
  onClose: () => void;
}

export const LearnMoreModal = ({ visible, vaspName, onClose }: Props) => {
  const buttons = (
    <Button text="Close" kind="quaternary" onClick={onClose} paddingY="short" />
  );

  return (
    <NwcModal visible={visible} onClose={onClose} buttons={buttons} width={560}>
      <ModalBody>
        <ModalTitle
          size="Small"
          content={`${vaspName} connects your UMA securely to third-party apps and services`}
        />
        <Section>
          <Title content="How does it work?" size="Large" />
          <SectionBody>
            <Body
              color="grayBlue43"
              content={`Unlock payments experiences on your favorite apps and services by connecting your ${vaspName} UMA.`}
            />
            <LinkText>
              <Body
                color="grayBlue43"
                content="UMA connections are powered by "
              />
              <Link target="_blank" href="https://nwc.dev/">
                Nostr Wallet Connect
              </Link>
              <Body
                color="grayBlue43"
                content=", enabling apps and services to securely interact with other UMAs or wallets."
              />
            </LinkText>
          </SectionBody>
        </Section>

        <Section>
          <Title content="Always in control" size="Large" />
          <Body
            color="grayBlue43"
            content="For every app or service you connect to your UMA you can change permissions, edit your spending limit, change when the connection expires, view your transactions, or revoke the connection at any time."
          />
        </Section>
      </ModalBody>
    </NwcModal>
  );
};

const ModalBody = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px["xl"]};
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.xs};
`;

const SectionBody = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.lg};
`;

const ModalTitle = styled(Headline)`
  padding-right: 20px;
`;

const LinkText = styled.div``;

const Link = styled.a`
  font-family: Manrope;
  font-size: 14px;
  font-weight: 500;
  line-height: 18px; /* 150% */
  color: #0068c9;
  text-decoration: none;
`;
