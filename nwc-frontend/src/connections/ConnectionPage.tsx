import styled from "@emotion/styled";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { TransactionTable } from "src/components/TransactionTable";
import { Header } from "./Header";
import { PermissionsList } from "src/permissions/PermissionsList";
import { useConnection } from "src/hooks/useConnection";
import { Shimmer } from "src/components/Shimmer";
import { Button, UnstyledButton } from "@lightsparkdev/ui/components";
import { Limit } from "./Limit";
import { useState } from "react";

export default function ConnectionPage({ appId }: { appId: string }) {
  const { connection, isLoading: isLoadingConnection } = useConnection({ appId });
  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);

  const handleEdit = () => {
    setIsEditLimitVisible(true);
  }

  return (
    <Main>
      <Header />
      <Content>
        <Section>
          <Title content="Permissions" />
          {isLoadingConnection ? <Shimmer width={200} height={20} /> : <PermissionsList permissions={connection.permissions} />}
        </Section>
        <Section>
          <SectionHeader>
            <Title content="Spending limit" />
            <Button kind="ghost" icon="Pencil" iconSide="left" text="Edit" onClick={handleEdit} />
          </SectionHeader>
          {isLoadingConnection ? <Shimmer width={200} height={20} /> : <Limit connection={connection} />}
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
  padding: ${Spacing["xl"]} ${Spacing["xl"]};

  &:not(:last-child) {
    border-bottom: 1px solid ${colors.gray90};
    padding-bottom: ${Spacing["xl"]};
  }
`;

const SectionHeader = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
`;

const EditButton = styled(UnstyledButton)`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${colors.gray95};
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: ${colors.gray90};
  }
`;
