import styled from "@emotion/styled";
import { Button, Icon, Modal } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Avatar } from "src/components/Avatar";
import { Connection } from "src/types/Connection";
import { formatTimestamp } from "src/utils/formatTimestamp";

export const Header = ({
  connection,
  updateConnection,
}: {
  connection: Connection;
  updateConnection: () => void;
}) => {
  const [isDisconnectModalVisible, setIsDisconnectModalVisible] =
    useState<boolean>(false);

  const handleDisconnect = () => {
    setIsDisconnectModalVisible(false);
    updateConnection({ ...connection, isActive: false });
  };

  const appDescription = connection.isActive
    ? `Connected on ${formatTimestamp(connection.createdAt)}`
    : `Disconnected on ${formatTimestamp(connection.disconnectedAt)}`;

  return (
    <Container>
      <Navigation to="/">
        <Icon name="ChevronLeft" width={12} />
        <HeaderText>Back to Connections</HeaderText>
      </Navigation>
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

const Navigation = styled(Link)`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const HeaderText = styled.span`
  color: ${({ theme }) => theme.link};
  text-align: center;
  font-size: 17px;
  font-style: normal;
  font-weight: 400;
  line-height: 22px; /* 129.412% */
  letter-spacing: -0.212px;
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
