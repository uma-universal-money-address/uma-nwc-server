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
    navigate(`/connection/${connection.connectionId}/update`);
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
          navigate(`/`);
        } else {
          setError(new Error(`Failed to disconnect ${connection.name}`));
        }
      })
      .catch((e) => {
        setError(e);
      });
  };

  let appDescription;
  if (connection.status === ConnectionStatus.ACTIVE) {
    if (connection.lastUsed) {
      appDescription = `Last used ${formatTimestamp(connection.lastUsed, {
        showTime: true,
      })}`;
    } else if (connection.expiresAt) {
      appDescription = `Disconnected on ${formatTimestamp(
        connection.expiresAt,
        {
          showTime: true,
        },
      )}`;
    }
  }

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
            <AppName title={connection.name}>{connection.name}</AppName>
            {appDescription && (
              <AppDescription>{appDescription}</AppDescription>
            )}
          </AppDetails>
        </AppSection>
        {connection.status === ConnectionStatus.ACTIVE ? (
          <Buttons>
            <Button
              kind="primary"
              icon={{ name: "Recycling" }}
              iconSide="left"
              text="Update"
              onClick={handleEdit}
              paddingY="short"
            />
            <Button
              text="Disconnect"
              kind="quaternary"
              icon={{ name: "Remove" }}
              onClick={() => setIsDisconnectModalVisible(true)}
              paddingY="short"
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
        description={`Disconnecting ${appInfo?.name ?? "this application"} will revoke its permissions and stop ${appInfo?.name ?? "it"} from sending money to and from your UMA.`}
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
  gap: ${Spacing.px.sm};
`;

const AppDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const AppName = styled.span`
  font-size: 32px;
  line-height: 40px; /* 125% */

  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: 310px;
  overflow: hidden;
`;

const AppDescription = styled.span`
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
`;

const Buttons = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.px.sm};
`;
