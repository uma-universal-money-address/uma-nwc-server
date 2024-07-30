import styled from "@emotion/styled";
import { Button, Icon, UnstyledButton } from "@lightsparkdev/ui/components";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import dayjs from "dayjs";
import { useState } from "react";
import { Avatar } from "src/components/Avatar";
import { Uma } from "src/components/Uma";
import { initializeConnection, useConnection } from "src/hooks/useConnection";
import { useUma } from "src/hooks/useUma";
import {
  ExpirationPeriod,
  LimitFrequency,
  Permission,
  PermissionType,
} from "src/types/Connection";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { PermissionsList } from "./PermissionsList";
import { ConnectionSettings, PersonalizePage } from "./PersonalizePage";

interface Props {
  appId: string;
  /** Defaults provided by the client app */
  clientAppDefaultSettings?: ConnectionSettings;
}

export const DEFAULT_CONNECTION_SETTINGS: ConnectionSettings = {
  permissionStates: [
    {
      permission: {
        type: PermissionType.SEND_PAYMENTS,
        description: "Send payments from your UMA",
      },
      enabled: true,
    },
    {
      permission: {
        type: PermissionType.READ_BALANCE,
        description: "Read your balance",
        optional: true,
      },
      enabled: false,
    },
    {
      permission: {
        type: PermissionType.READ_TRANSACTIONS,
        description: "Read transaction history",
        optional: true,
      },
      enabled: false,
    },
  ],
  amountInLowestDenom: 50000,
  limitFrequency: LimitFrequency.MONTHLY,
  limitEnabled: true,
  expirationPeriod: ExpirationPeriod.YEAR,
};

export const PermissionsPage = ({ appId, clientAppDefaultSettings }: Props) => {
  const {
    connection,
    updateConnection,
    isLoading: isLoadingConnection,
  } = useConnection({ appId });
  const { uma, isLoading: isLoadingUma } = useUma();

  const [isPersonalizeVisible, setIsPersonalizeVisible] =
    useState<boolean>(false);
  const [connectionSettings, setConnectionSettings] =
    useState<ConnectionSettings>(
      clientAppDefaultSettings || DEFAULT_CONNECTION_SETTINGS,
    );
  const [isConnecting, setIsConnecting] = useState<boolean>(false);

  if (isLoadingConnection || isLoadingUma) {
    return (
      <Container>
        <Title content="Loading..." />
      </Container>
    );
  }

  const {
    name,
    domain,
    avatar,
    amountInLowestDenom,
    limitFrequency,
    limitEnabled,
    currency,
    verified,
  } = connection;

  const handleShowPersonalize = () => {
    setIsPersonalizeVisible(true);
  };

  const handleUpdateConnectionSettings = (
    connectionSettings: ConnectionSettings,
  ) => {
    setConnectionSettings(connectionSettings);
    setIsPersonalizeVisible(false);
  };

  const handleReset = () => {
    setConnectionSettings(
      clientAppDefaultSettings || DEFAULT_CONNECTION_SETTINGS,
    );
    setIsPersonalizeVisible(false);
  };

  const handleSubmit = () => {
    if (!connection) {
      return;
    }

    const today = dayjs();
    const expiration = today
      .add(1, connectionSettings.expirationPeriod)
      .toISOString();

    async function submitConnection() {
      setIsConnecting(true);
      await initializeConnection({
        appId: connection.appId,
        name: connection.name,
        currency: connection.currency,
        permissions: connectionSettings.permissionStates
          .filter((permissionState) => permissionState.enabled)
          .map((permissionState) => permissionState.permission),
        amountInLowestDenom: connectionSettings.amountInLowestDenom,
        limitFrequency: connectionSettings.limitFrequency,
        limitEnabled: connectionSettings.limitEnabled,
        expiration: expiration,
      });
      setIsConnecting(false);
    }

    submitConnection();
  };

  if (isPersonalizeVisible) {
    return (
      <PersonalizePage
        connection={connection}
        connectionSettings={connectionSettings}
        updateConnectionSettings={handleUpdateConnectionSettings}
        onBack={() => setIsPersonalizeVisible(false)}
        onReset={handleReset}
      />
    );
  }

  const permissions: (Permission | string)[] =
    connectionSettings.permissionStates
      .filter((permissionState) => permissionState.enabled)
      .map((permissionState) => permissionState.permission);
  if (connectionSettings.limitEnabled) {
    permissions.push(
      `Set a ${formatConnectionString({ currency, limitFrequency: connectionSettings.limitFrequency, amountInLowestDenom: connectionSettings.amountInLowestDenom })} spend limit`,
    );
  }
  if (connectionSettings.expirationPeriod !== ExpirationPeriod.NONE) {
    permissions.push(
      `Expire connection in 1 ${connectionSettings.expirationPeriod.toLowerCase()}`,
    );
  }

  const header = (
    <Header>
      <VaspLogo src="/vasp.svg" width={32} height={32} />
      <UnstyledButton>
        <Icon name="Close" width={8} />
      </UnstyledButton>
    </Header>
  );
  return (
    <Container>
      {header}
      <Intro>
        <Title content="Connect your UMA" />
        <Uma uma={uma} />
      </Intro>

      <PermissionsContainer>
        <PermissionsDescription>
          <AppSection>
            <Avatar src={avatar} size={48} />
            <AppDetails>
              <AppName>
                {name}
                {verified ? (
                  <VerifiedBadge>
                    <Icon name="CheckmarkCircleTier3" width={20} />
                  </VerifiedBadge>
                ) : null}
              </AppName>
              <AppDomain>{domain}</AppDomain>
            </AppDetails>
          </AppSection>
          <Permissions>
            <Label size="Large" content="Would like to" />
            <PermissionsList permissions={permissions} />
          </Permissions>
        </PermissionsDescription>
        <Personalize onClick={handleShowPersonalize}>
          <PersonalizeDescription>
            Personalize permissions
          </PersonalizeDescription>
          <Icon name="CaretRight" width={12} />
        </Personalize>
      </PermissionsContainer>

      <ButtonSection>
        <Button
          text="Connect UMA"
          kind="primary"
          fullWidth
          onClick={handleSubmit}
          loading={isConnecting}
          disabled={isLoadingConnection || !connection}
        />
        <Button
          text="Cancel"
          kind="secondary"
          fullWidth
          disabled={isConnecting}
        />
      </ButtonSection>
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-self: center;
  gap: 24px;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;

  max-width: 345px;
`;

const Header = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
  justify-content: space-between;
`;

const VaspLogo = styled.img``;

const Intro = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xs};
  width: 100%;
`;

const PermissionsContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  border: 0.5px solid #c0c9d6;
  border-radius: 8px;
  background: ${colors.white};
`;

const PermissionsDescription = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xl};
  width: 100%;
  border-bottom: 0.5px solid #c0c9d6;
  padding: ${Spacing.lg};
`;

const AppSection = styled.div`
  display: flex;
  flex-direction: row;
  gap: 16px;
  align-items: center;
`;

const AppDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const AppName = styled.div`
  display: flex;
  flex-direction: row;
  gap: 4px;
`;

const AppDomain = styled.div`
  color: #686a72;
  font-size: 14px;
`;

const VerifiedBadge = styled.div`
  color: #00d4ff;
  font-size: 12px;
`;

const Permissions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.sm};
`;

const Personalize = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: ${Spacing.lg};
  cursor: pointer;
`;

const PersonalizeDescription = styled.div`
  color: #686a72;
  font-size: 16px;
`;

const ButtonSection = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 345px;
  width: 100%;
  gap: 16px;
`;
