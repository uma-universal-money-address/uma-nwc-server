import styled from "@emotion/styled";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { TransactionTable } from "src/components/TransactionTable";
import { Header } from "./Header";

export default function ConnectionPage({ appId }: { appId: string }) {
  return (
    <Main>
      <Header />
      <Title content="Permissions" />
      <Title content="Spending limit" />
      <Title content="Transactions" />
      <TransactionTable appId={appId} />
    </Main>
  );
}

const Main = styled.main`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: ${colors.white};
  padding: ${Spacing.md} ${Spacing["2xl"]};
  border-radius: 24px;
`;
