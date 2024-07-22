import styled from "@emotion/styled";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { TransactionTable } from "src/components/TransactionTable";
import { Header } from "./Header";
import { PermissionsList } from "src/permissions/PermissionsList";
import { useConnection } from "src/hooks/useConnection";
import { Shimmer } from "src/components/Shimmer";

export default function ConnectionPage({ appId }: { appId: string }) {
  const { connection, isLoading: isLoadingConnection } = useConnection({ appId });

  return (
    <Main>
      <Header />
      <Content>
        <Section>
          <Title content="Permissions" />
          {isLoadingConnection ? <Shimmer width={200} height={20} /> : <PermissionsList permissions={connection.permissions} />}
        </Section>
        <Section>
          <Title content="Spending limit" />

        </Section>
        <Section>
          <Title content="Transactions" />
          <TransactionTable appId={appId} />
        </Section>
      </Content>
    </Main>
  );
}

const Main = styled.main`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;

  border-radius: 24px;
  background: ${colors.white};
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.lg};
  width: 100%;
  padding: ${Spacing["2xl"]} ${Spacing["2xl"]};

  &:not(:last-child) {
    border-bottom: 1px solid ${colors.gray90};
    padding-bottom: ${Spacing["2xl"]};
  }
`;
