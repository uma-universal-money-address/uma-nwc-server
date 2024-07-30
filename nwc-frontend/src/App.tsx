import styled from "@emotion/styled";
import { Button } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import {
  ConnectionTable,
  LoadingConnectionRow,
} from "src/components/ConnectionTable";
import { LearnMoreModal } from "./LearnMoreModal";
import { useConnections } from "./hooks/useConnections";

function App() {
  const [isLearnMoreVisible, setIsLearnMoreVisible] = useState<boolean>(false);
  const {
    connections,
    isLoading: isLoadingConnections,
    error,
  } = useConnections();
  const vasp = "Exchange";

  const handleLearnMore = () => {
    setIsLearnMoreVisible(true);
  };

  const activeConnections = connections?.filter(
    (connection) => connection.isActive,
  );
  const archivedConnections = connections?.filter(
    (connection) => !connection.isActive,
  );

  return (
    <Main>
      <Section>
        <Intro>
          <Title size="Large" content="Manage your UMA connections" />
          <Description>
            <Body content="Review permissions, edit spending limits, and view transactions for the third-party apps and services connected to your UMA. " />
            <Button
              text="Learn more"
              kind="ghost"
              onClick={handleLearnMore}
              typography={{ type: "Body", color: "blue39" }}
              size="Medium"
            />
          </Description>
        </Intro>
        <Content>
          {isLoadingConnections ? (
            <>
              <LoadingConnectionRow key="loader-1" shimmerWidth={30} />
              <LoadingConnectionRow key="loader-2" shimmerWidth={10} />
              <LoadingConnectionRow key="loader-3" shimmerWidth={20} />
            </>
          ) : (
            <ConnectionTable connections={activeConnections} />
          )}
          {error ? (
            <Container>{`Error loading connections: ${error}`}</Container>
          ) : null}
        </Content>
      </Section>
      <Button
        icon="Plus"
        text="Manual connection"
        kind="primary"
        href="/connection/new"
      />

      {isLoadingConnections || !archivedConnections.length ? null : (
        <Section>
          <Intro>
            <Title size="Large" content="Archived connections" />
            <Description>
              <Body content="You can still review past transactions on connections" />
            </Description>
          </Intro>
          <Content>
            <ConnectionTable connections={archivedConnections} />
          </Content>
        </Section>
      )}

      <LearnMoreModal
        visible={isLearnMoreVisible}
        vaspName={vasp}
        onClose={() => setIsLearnMoreVisible(false)}
      />
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

const Description = styled.div``;

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

export default App;
