import styled from "@emotion/styled";
import { Button, Modal } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Avatar } from "src/components/Avatar";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";
import { Connection } from "src/types/Connection";
import { formatTimestamp } from "src/utils/formatTimestamp";
import { Nav } from "./Nav";

export const ConnectionHeader = ({
  connection,
  updateConnection,
}: {
  connection: Connection;
  updateConnection: () => Promise<boolean>;
}) => {
  const [isDisconnectModalVisible, setIsDisconnectModalVisible] =
    useState<boolean>(false);
  const { setSuccessMessage, setError } = useGlobalNotificationContext();

  const handleDisconnect = () => {
    setIsDisconnectModalVisible(false);
    updateConnection({ ...connection, isActive: false })
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

  const appDescription = connection.isActive
    ? `Connected on ${formatTimestamp(connection.createdAt)}`
    : `Disconnected on ${formatTimestamp(connection.disconnectedAt)}`;

  return (
    <Container>
      <Nav />
      <AppAndDisconnect>
        <AppSection>
          <Avatar size={72} src={connection.avatar} />
          <AppDetails>
            <AppName>{connection.name}</AppName>
            <AppDescription>{appDescription}</AppDescription>
          </AppDetails>
        </AppSection>
        {connection.isActive ? (
          <Button
            text="Disconnect"
            icon="Remove"
            onClick={() => setIsDisconnectModalVisible(true)}
          />
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
  padding: 16px 10px;
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
