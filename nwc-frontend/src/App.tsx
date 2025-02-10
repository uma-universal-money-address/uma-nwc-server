import styled from "@emotion/styled";
import { Button } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Headline } from "@lightsparkdev/ui/components/typography/Headline";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ConnectionTable,
  LoadingConnectionRow,
} from "src/components/ConnectionTable";
import { useConnections } from "./hooks/useConnections";
import { LearnMoreModal } from "./LearnMoreModal";
import { Routes, generatePath } from "./routes/Routes";
import { ConnectionStatus } from "./types/Connection";
import { getConfig } from "./utils/getConfig";

function App() {
  const navigate = useNavigate();
  const [isLearnMoreVisible, setIsLearnMoreVisible] = useState<boolean>(false);
  const {
    connections,
    isLoading: isLoadingConnections,
    error,
  } = useConnections();
  const { vaspName } = getConfig();

  const handleLearnMore = () => {
    setIsLearnMoreVisible(true);
  };

  const activeOrPendingConnections = connections?.filter(
    (connection) => connection.status !== ConnectionStatus.INACTIVE,
  );
  const archivedConnections = connections?.filter(
    (connection) => connection.status === ConnectionStatus.INACTIVE,
  );

  return (
    <Main>
      <Section>
        <Intro>
          <Headline size="Large" content="Manage your UMA connections" />
          <Description>
            <Body
              size="Large"
              content="Review permissions, edit spending limits, and view transactions for the third-party apps and services connected to your UMA. "
              color="grayBlue57"
            />
            <Button
              text="Learn more"
              kind="ghost"
              onClick={handleLearnMore}
              typography={{ type: "Body", color: "blue39" }}
              size="Large"
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
            <ConnectionTable connections={activeOrPendingConnections || []} />
          )}
          {error ? <div>{`Error loading connections: ${error}`}</div> : null}
        </Content>
        {activeOrPendingConnections?.length ? (
          <Button
            icon={{ name: "Plus" }}
            text="Manual connection"
            kind="primary"
            onClick={() => navigate(generatePath(Routes.ConnectionNew, {}))}
          />
        ) : null}
      </Section>

      {isLoadingConnections || !archivedConnections?.length ? null : (
        <Section>
          <Intro>
            <Headline size="Small" content="Archived connections" />
            <Description>
              <Body
                size="Large"
                content="You can still review past transactions on connections"
                color="grayBlue57"
              />
            </Description>
          </Intro>
          <Content>
            <ConnectionTable connections={archivedConnections || []} />
          </Content>
        </Section>
      )}

      <LearnMoreModal
        visible={isLearnMoreVisible}
        vaspName={vaspName}
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
  gap: ${Spacing.px["5xl"]};
`;

const Intro = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const Description = styled.div``;

const Content = styled.div`
  padding: ${Spacing.px["3xl"]} ${Spacing.px.xl};
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 32px;

  background: ${colors.white};
  padding: ${Spacing.px.md} ${Spacing.px["2xl"]};
  border-radius: 24px;
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.xl};
  margin-top: ${Spacing.px.xl};
`;

export default App;
