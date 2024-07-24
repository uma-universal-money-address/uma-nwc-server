import styled from "@emotion/styled";
import { Button } from "@lightsparkdev/ui/components";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Shimmer } from "src/components/Shimmer";
import { TransactionTable } from "src/components/TransactionTable";
import { useConnection } from "src/hooks/useConnection";
import { EditLimit } from "src/permissions/EditLimit";
import { PermissionsList } from "src/permissions/PermissionsList";
import { Header } from "./Header";
import { Limit } from "./Limit";

export default function ConnectionPage({ appId }: { appId: string }) {
  const {
    connection,
    updateConnection,
    isLoading: isLoadingConnection,
  } = useConnection({ appId });
  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);

  const handleEdit = () => {
    setIsEditLimitVisible(true);
  };

  const handleSubmitEditLimit = ({
    amountInLowestDenom,
    frequency,
    enabled,
  }: {
    amountInLowestDenom: number;
    frequency: LimitFrequency;
    enabled: boolean;
  }) => {
    updateConnection({
      amountInLowestDenom,
      limitFrequency: frequency,
      limitEnabled: enabled,
    });
    setIsEditLimitVisible(false);
  };

  return (
    <Main>
      {connection ? (
        <Header connection={connection} updateConnection={updateConnection} />
      ) : null}
      <Content>
        {!isLoadingConnection && connection?.isActive ? (
          <>
            <Section>
              <Title content="Permissions" />
              {isLoadingConnection ? (
                <Shimmer width={200} height={20} />
              ) : (
                <PermissionsList permissions={connection.permissions} />
              )}
            </Section>
            <Section>
              <SectionHeader>
                <Title content="Spending limit" />
                <Button
                  kind="ghost"
                  icon="Pencil"
                  iconSide="left"
                  text="Edit"
                  onClick={handleEdit}
                  disabled={isLoadingConnection}
                  typography={{ color: "blue39" }}
                />
              </SectionHeader>
              {isLoadingConnection ? (
                <Shimmer width={200} height={20} />
              ) : (
                <Limit connection={connection} />
              )}
            </Section>
          </>
        ) : null}
        <Section>
          <Title content="Transactions" />
          <TransactionTable appId={appId} />
        </Section>
      </Content>
      {isLoadingConnection ? null : (
        <EditLimit
          title="Edit spending limit"
          visible={isEditLimitVisible}
          amountInLowestDenom={connection.amountInLowestDenom}
          currency={connection.currency}
          frequency={connection.limitFrequency}
          enabled={connection?.limitEnabled}
          handleCancel={() => setIsEditLimitVisible(false)}
          handleSubmit={handleSubmitEditLimit}
        />
      )}
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

  * {
    border: none !important;
  }
`;
