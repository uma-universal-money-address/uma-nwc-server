import styled from "@emotion/styled";
import { Button, Icon, UnstyledButton } from "@lightsparkdev/ui/components";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import dayjs from "dayjs";
import { useState } from "react";
import { useLoaderData, useNavigate } from "react-router-dom";
import { Avatar } from "src/components/Avatar";
import { Uma } from "src/components/Uma";
import {
  initializeConnection,
  updateConnection,
} from "src/hooks/useConnection";
import { ExpirationPeriod, Permission } from "src/types/Connection";
import { PermissionPageLoaderData } from "src/types/PermissionPageLoaderData";
import { useAuth } from "src/utils/auth";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { PermissionsList } from "./PermissionsList";
import { ConnectionSettings, PersonalizePage } from "./PersonalizePage";
import { AppInfo } from "src/types/AppInfo";

async function initConnection({
  appInfo,
  connectionSettings,
  currencyCode,
  redirectUri,
  expiration,
}: {
  appInfo: AppInfo;
  connectionSettings: ConnectionSettings;
  currencyCode: string;
  redirectUri: string;
  expiration: string;
}) {
  const { code, state, error } = await initializeConnection({
    clientId: appInfo.clientId,
    name: appInfo.name,
    currencyCode,
    permissions: connectionSettings.permissionStates
      .filter((permissionState) => permissionState.enabled)
      .map((permissionState) => permissionState.permission.type),
    amountInLowestDenom: connectionSettings.amountInLowestDenom,
    limitFrequency: connectionSettings.limitFrequency,
    limitEnabled: connectionSettings.limitEnabled,
    expiration,
  });
  if (error) {
    // TODO: Show an error toast.
    console.error(error);
    return;
  }
  console.log(`Redirecting to ${redirectUri}?code=${code}&state=${state}`);
  window.location.href = `${redirectUri}?code=${code}&state=${state}`;
}

export const PermissionsPage = () => {
  const {
    appInfo,
    oauthParams,
    connection,
    connectionSettings: initialConnectionSettings,
    defaultCurrency,
  } = useLoaderData() as PermissionPageLoaderData;
  const auth = useAuth();
  const uma = auth.getUmaAddress();
  const navigate = useNavigate();

  const [isPersonalizeVisible, setIsPersonalizeVisible] =
    useState<boolean>(false);
  const [connectionSettings, setConnectionSettings] =
    useState<ConnectionSettings>(initialConnectionSettings);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const { name, domain, avatar, verified } = appInfo;

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
    setConnectionSettings(initialConnectionSettings);
    setIsPersonalizeVisible(false);
  };

  const handleSubmit = () => {
    const today = dayjs();
    const expiration = today
      .add(1, connectionSettings.expirationPeriod.toLowerCase())
      .toISOString();

    setIsSubmitting(true);
    if (oauthParams) {
      initConnection({
        appInfo,
        connectionSettings,
        currencyCode: defaultCurrency.code,
        redirectUri: oauthParams.redirectUri,
        expiration,
      });
    } else {
      updateConnection({
        connectionId: connection.connectionId,
        amountInLowestDenom: connectionSettings.amountInLowestDenom,
        limitFrequency: connectionSettings.limitFrequency,
        limitEnabled: connectionSettings.limitEnabled,
        status: connection.status,
        expiration,
      });
      navigate(`/connection/${connection.connectionId}`);
    }
  };

  if (isPersonalizeVisible) {
    return (
      <PersonalizePage
        appInfo={appInfo}
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
      `Set a ${formatConnectionString({ currency: defaultCurrency, limitFrequency: connectionSettings.limitFrequency, amountInLowestDenom: connectionSettings.amountInLowestDenom })} spend limit`,
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
        <Uma uma={uma ?? ""} />
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
          loading={isSubmitting}
        />
        <Button
          text="Cancel"
          kind="secondary"
          fullWidth
          disabled={isSubmitting}
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
