import styled from "@emotion/styled";
import { Button } from "@lightsparkdev/ui/components";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { useParams } from "react-router-dom";
import { Shimmer } from "src/components/Shimmer";
import { TransactionTable } from "src/components/TransactionTable";
import { useConnection } from "src/hooks/useConnection";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";
import { EditLimit } from "src/permissions/EditLimit";
import { PermissionsList } from "src/permissions/PermissionsList";
import { ConnectionStatus } from "src/types/Connection";
import { ConnectionHeader } from "./ConnectionHeader";
import { Limit } from "./Limit";
import { PendingConnectionPage } from "./PendingConnectionPage";

export default function ConnectionPage() {
  const { appId } = useParams<{ appId: string }>();
  const {
    connection,
    updateConnection,
    isLoading: isLoadingConnection,
  } = useConnection({ appId });
  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);
  const { setSuccessMessage, setError } = useGlobalNotificationContext();

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
      status: connection?.status,
    })
      .then((succeeded) => {
        if (succeeded) {
          setSuccessMessage("Spending limit updated successfully");
        } else {
          setError(new Error("Failed to update spending limit"));
        }
      })
      .catch((e) => {
        setError(e);
      });
    setIsEditLimitVisible(false);
  };

  if (connection?.status === ConnectionStatus.PENDING) {
    return (
      <PendingConnectionPage
        name={connection.name}
        permissions={connection.permissions}
      />
    );
  }

  return (
    <>
      {connection ? (
        <ConnectionHeader
          connection={connection}
          updateConnection={updateConnection}
        />
      ) : null}
      <Content>
        {!isLoadingConnection &&
        connection?.status === ConnectionStatus.ACTIVE ? (
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
    </>
  );
}

const Content = styled.div`
  display: flex;
  flex-direction: column;

  border-radius: 24px;
  background: ${colors.white};

  & > *:not(:last-child) {
    border-bottom: 1px solid ${colors.gray90};
    padding-bottom: ${Spacing["xl"]};
  }
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.lg};
  width: 100%;
  padding: ${Spacing["xl"]};
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
