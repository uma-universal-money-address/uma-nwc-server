import styled from "@emotion/styled";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { ConnectionTable } from "src/components/ConnectionTable";

function App() {
  return (
    <Main>
      <Intro>
        <Title size="Large" content="Manage your UMA connections" />
        <Body
          content={[
            "You connected your UMA to these third-party apps and services. ",
            { text: "Learn more", href: "/faq", color: "#0068C9" },
          ]}
        />
      </Intro>
      <Content>
        <ConnectionTable />
      </Content>
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

export default App;
