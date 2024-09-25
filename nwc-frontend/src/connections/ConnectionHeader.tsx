import styled from "@emotion/styled";
import { Button, Modal } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Avatar } from "src/components/Avatar";
import { useAppInfo } from "src/hooks/useAppInfo";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";
import { type Connection, ConnectionStatus } from "src/types/Connection";
import { formatTimestamp } from "src/utils/formatTimestamp";

export const ConnectionHeader = ({
  connection,
  updateConnection,
}: {
  connection: Connection;
  updateConnection: (connection: Connection) => Promise<boolean>;
}) => {
  const navigate = useNavigate();
  const [isDisconnectModalVisible, setIsDisconnectModalVisible] =
    useState<boolean>(false);
  const { setSuccessMessage, setError } = useGlobalNotificationContext();
  const { appInfo, isLoading: isLoadingAppInfo } = useAppInfo({
    clientId: connection.clientId,
  });

  const handleEdit = () => {
    navigate(`/connection/update/${connection.connectionId}`);
  };

  const handleDisconnect = () => {
    setIsDisconnectModalVisible(false);
    updateConnection({
      ...connection,
      status: ConnectionStatus.INACTIVE,
    })
      .then((succeeded) => {
        if (succeeded) {
          setSuccessMessage(`${connection.name} disconnected successfully`);
        } else {
          setError(new Error(`Failed to disconnect ${connection.name}`));
        }
      })
      .catch((e) => {
        setError(e);
      });
  };

  const appDescription =
    connection.status === ConnectionStatus.ACTIVE
      ? `Connected on ${formatTimestamp(connection.createdAt)}`
      : `Disconnected on ${formatTimestamp(connection.expiresAt!)}`;

  return (
    <Container>
      <AppAndDisconnect>
        <AppSection>
          <Avatar
            size={72}
            src={appInfo?.avatar ?? ""}
            isLoading={isLoadingAppInfo}
          />
          <AppDetails>
            <AppName>{connection.name}</AppName>
            <AppDescription>{appDescription}</AppDescription>
          </AppDetails>
        </AppSection>
        {connection.status === ConnectionStatus.ACTIVE ? (
          <Buttons>
            <Button
              kind="primary"
              icon="Restart"
              iconSide="left"
              text="Update"
              onClick={handleEdit}
            />
            <Button
              text="Disconnect"
              icon="Remove"
              onClick={() => setIsDisconnectModalVisible(true)}
            />
          </Buttons>
        ) : null}
      </AppAndDisconnect>

      <Modal
        smKind="drawer"
        visible={isDisconnectModalVisible}
        onClose={() => setIsDisconnectModalVisible(false)}
        onCancel={() => setIsDisconnectModalVisible(false)}
        onSubmit={handleDisconnect}
        submitText="Confirm"
        cancelText="Cancel"
        title={`Disconnect ${connection.name}?`}
        description="Disconnecting WhatsApp will revoke its permissions and stop  WhatsApp from sending money to and from your UMA."
      ></Modal>
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
`;

const AppAndDisconnect = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
`;

const AppSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${Spacing.sm};
`;

const AppDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const AppName = styled.span`
  font-size: 32px;
  font-style: normal;
  line-height: 40px; /* 125% */
`;

const AppDescription = styled.span`
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
`;

const Buttons = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.sm};
`;
