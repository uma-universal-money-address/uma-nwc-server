import styled from "@emotion/styled";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useParams } from "react-router-dom";
import { Shimmer } from "src/components/Shimmer";
import { TransactionTable } from "src/components/TransactionTable";
import { useConnection } from "src/hooks/useConnection";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";
import { PermissionsList } from "src/permissions/PermissionsList";
import { ConnectionStatus } from "src/types/Connection";
import { ConnectionHeader } from "./ConnectionHeader";
import { Limit } from "./Limit";
import { PendingConnectionPage } from "./PendingConnectionPage";

export default function ConnectionPage() {
  const { connectionId } = useParams<{ connectionId: string }>();
  if (!connectionId) {
    return (
      <Content>
        <Title content="No connection ID requested" />
        <Section>
          <p>
            Please provide a connection ID in the URL to view the connection
            details.
          </p>
        </Section>
      </Content>
    )
  }
  const {
    connection,
    updateConnection,
    isLoading: isLoadingConnection,
  } = useConnection({ connectionId });
  const { setSuccessMessage, setError } = useGlobalNotificationContext();

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
          <TransactionTable connectionId={connectionId} />
        </Section>
      </Content>
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
