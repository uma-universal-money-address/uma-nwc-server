import styled from "@emotion/styled";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useParams } from "react-router-dom";
import { Shimmer } from "src/components/Shimmer";
import { TransactionTable } from "src/components/TransactionTable";
import { useConnection } from "src/hooks/useConnection";
import { PermissionsList } from "src/permissions/PermissionsList";
import { ConnectionStatus } from "src/types/Connection";
import { formatTimestamp } from "src/utils/formatTimestamp";
import { ConnectionHeader } from "./ConnectionHeader";
import { Limit } from "./Limit";
import { PendingConnectionPage } from "./PendingConnectionPage";

export default function ConnectionPage() {
  const { connectionId } = useParams<{ connectionId: string }>();
  const {
    connection,
    updateConnection,
    isLoading: isLoadingConnection,
  } = useConnection({ connectionId: connectionId ?? "" });
  if (!connectionId) {
    return (
      <Content>
        <Title content="Connection ID must be provided." />
      </Content>
    );
  }

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
              <Title size="Large" content="Permissions" />
              {isLoadingConnection ? (
                <Shimmer width={200} height={20} />
              ) : (
                <PermissionsList permissions={connection.permissions} />
              )}
            </Section>
            <Section>
              <SectionHeader>
                <Title size="Large" content="Spending limit" />
              </SectionHeader>
              {isLoadingConnection ? (
                <Shimmer width={200} height={20} />
              ) : (
                <Limit connection={connection} />
              )}
            </Section>
            <Section>
              <SectionHeader>
                <Title size="Large" content="Expiration date" />
              </SectionHeader>
              {isLoadingConnection ? (
                <Shimmer width={200} height={20} />
              ) : (
                <ExpirationText>
                  <ExpiresOn>
                    {connection.expiresAt
                      ? `Expires on ${formatTimestamp(connection.expiresAt)}`
                      : "No expiration set"}
                  </ExpiresOn>
                  <ConnectedOn>
                    {`Connected on ${formatTimestamp(connection.createdAt, { showTime: true })}`}
                  </ConnectedOn>
                </ExpirationText>
              )}
            </Section>
          </>
        ) : null}
        <Section>
          <Title size="Large" content="Transactions" />
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
    padding-bottom: ${Spacing.px["xl"]};
  }
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.lg};
  width: 100%;
  padding: ${Spacing.px["xl"]};
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

const ExpirationText = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const ExpiresOn = styled.span`
  font-size: 16px;
  font-weight: 700;
  line-height: 24px; /* 150% */
`;

const ConnectedOn = styled.span`
  font-size: 16px;
  font-weight: 500;
  line-height: 24px; /* 150% */
`;
