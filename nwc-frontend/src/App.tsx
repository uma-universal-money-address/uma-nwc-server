import styled from "@emotion/styled";
import { Button, Modal } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { ConnectionTable } from "src/components/ConnectionTable";

function App() {
  const [isLearnMoreVisible, setIsLearnMoreVisible] = useState<boolean>(false);
  const vasp = "Exchange";

  const handleLearnMore = () => {
    setIsLearnMoreVisible(true);
  };

  return (
    <Main>
      <Intro>
        <Title size="Large" content="Manage your UMA connections" />
        <Description>
          <Body content="Review permissions, edit spending limits, and view transactions for the third-party apps and services connected to your UMA. "/>
          <Button text="Learn more" kind="ghost" onClick={handleLearnMore} typography={{ type: "Body", color: "blue39" }} size="Medium" />
        </Description>
      </Intro>
      <Content>
        <ConnectionTable />
      </Content>
      <Modal
        smKind="drawer"
        visible={isLearnMoreVisible}
        cancelText="Close"
        onClose={() => setIsLearnMoreVisible(false)}
        onCancel={() => setIsLearnMoreVisible(false)}
        title={`How ${vasp} connects your UMA securely to third-party apps and services`}
      >
        <Section>
          <Title content="How does it work?" size="Medium" />
          <Body color="grayBlue43" content={`You can unlock payments experiences on the apps and services you use by connecting your ${vasp} UMA.`} />
          <Body color="grayBlue43" content={[
            "UMA connections are powered by ",
            { text: "Nostr Wallet Connect", externalLink: "https://nwc.dev/", color: "blue39" },
            ", a standardized protocol that enables apps and services to securely interact with other UMAs or wallets.",
          ]} />
        </Section>

        <Section>
          <Title content="You are in control" size="Medium" />
          <Body color="grayBlue43" content="For each app or service that you connect to your UMA, you can review permissions, edit your spending limit, view transactions, or disconnect your UMA." />
        </Section>
      </Modal>
    </Main>
  );
}

const Main = styled.main`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  gap: ${Spacing["2xl"]};
`;

const Intro = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.sm};
`;

const Description = styled.div`
`;

const Content = styled.div`
  padding: ${Spacing["3xl"]} ${Spacing.xl};
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 32px;

  background: ${colors.white};
  padding: ${Spacing.md} ${Spacing["2xl"]};
  border-radius: 24px;
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xs};
  margin-top: ${Spacing["xl"]};
`;

const IntroSection = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xs};
`;

export default App;
