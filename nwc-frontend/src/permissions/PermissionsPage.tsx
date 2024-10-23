import styled from "@emotion/styled";
import { Button, Icon } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import dayjs, { type ManipulateType } from "dayjs";
import { useState } from "react";
import { useLoaderData, useNavigate } from "react-router-dom";
import { Avatar } from "src/components/Avatar";
import { Uma } from "src/components/Uma";
import {
  initializeConnection,
  updateConnection,
} from "src/hooks/useConnection";
import { type AppInfo } from "src/types/AppInfo";
import { ExpirationPeriod, type Permission } from "src/types/Connection";
import {
  isLoaderDataFromConnection,
  isLoaderDataFromUrl,
  type PermissionPageLoaderData,
} from "src/types/PermissionPageLoaderData";
import { getAuth } from "src/utils/auth";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { PermissionsList } from "./PermissionsList";
import { type ConnectionSettings, PersonalizePage } from "./PersonalizePage";

async function initConnection({
  appInfo,
  connectionSettings,
  currencyCode,
  redirectUri,
  expiration,
  clientState,
  codeChallenge,
}: {
  appInfo: AppInfo;
  connectionSettings: ConnectionSettings;
  currencyCode: string;
  redirectUri: string;
  codeChallenge: string;
  expiration: string | undefined;
  clientState: string | undefined;
}) {
  const { code, error } = await initializeConnection({
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
    redirectUri,
    clientState,
    codeChallenge,
  });
  if (error) {
    // TODO: Show an error toast.
    console.error(error);
    return;
  }
  if (!code) {
    // TODO: Show an error toast.
    console.error(`Missing code in connection response: code - ${code}`);
    return;
  }
  const fullRedirectUri =
    `${redirectUri}?code=${code}` +
    (clientState !== undefined && `&state=${clientState}`);
  console.log(`Redirecting to ${fullRedirectUri}`);
  window.location.href = fullRedirectUri;
}

export const PermissionsPage = () => {
  const loaderData = useLoaderData() as PermissionPageLoaderData;
  const { appInfo, connectionSettings: initialConnectionSettings } = loaderData;
  const auth = getAuth();
  const uma = auth.getUmaAddress();
  const currency = auth.getCurrency();
  const navigate = useNavigate();

  const [isPersonalizeVisible, setIsPersonalizeVisible] =
    useState<boolean>(false);
  const [connectionSettings, setConnectionSettings] =
    useState<ConnectionSettings>(initialConnectionSettings);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

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

  const handleBack = () => {
    if (isLoaderDataFromUrl(loaderData)) {
      window.location.href = loaderData.oauthParams.redirectUri;
    } else {
      navigate(`/connection/${loaderData.connection.connectionId}`);
    }
  };

  const handleSubmit = () => {
    const today = dayjs();
    const expiration =
      connectionSettings.expirationPeriod === ExpirationPeriod.NONE
        ? undefined
        : today
            .add(
              1,
              connectionSettings.expirationPeriod.toLowerCase() as ManipulateType,
            )
            .toISOString();

    setIsSubmitting(true);
    if (isLoaderDataFromUrl(loaderData)) {
      initConnection({
        appInfo: loaderData.appInfo,
        connectionSettings,
        currencyCode: currency?.code ?? "SAT",
        redirectUri: loaderData.oauthParams.redirectUri,
        clientState: loaderData.oauthParams.state,
        codeChallenge: loaderData.oauthParams.codeChallenge,
        expiration,
      });
    } else {
      updateConnection({
        connectionId: loaderData.connection.connectionId,
        amountInLowestDenom: connectionSettings.amountInLowestDenom,
        limitFrequency: connectionSettings.limitFrequency,
        limitEnabled: connectionSettings.limitEnabled,
        status: loaderData.connection.status,
        expiration,
      });
      navigate(`/connection/${loaderData.connection.connectionId}`);
    }
  };

  if (isPersonalizeVisible) {
    return (
      <PersonalizePage
        appInfo={appInfo}
        connection={
          isLoaderDataFromConnection(loaderData)
            ? loaderData.connection
            : undefined
        }
        connectionSettings={connectionSettings}
        updateConnectionSettings={handleUpdateConnectionSettings}
        onBack={() => setIsPersonalizeVisible(false)}
        onReset={handleReset}
        permissionsEditable={loaderData.permissionsEditable}
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
    </Header>
  );
  return (
    <Container>
      {isLoaderDataFromUrl(loaderData) ? (
        <>
          {header}
          <Intro>
            <ConnectYourUma>Connect your UMA</ConnectYourUma>
            <Uma uma={uma ?? undefined} />
          </Intro>
        </>
      ) : null}

      <PermissionsContainer>
        <PermissionsDescription>
          <AppSection>
            <Avatar src={appInfo?.avatar} size={48} />
            <AppDetails>
              <AppName>
                {appInfo && (
                  <>
                    <Title content={appInfo.name} />
                    {appInfo.verified && (
                      <VerifiedBadge>
                        <Icon name="NonagonCheckmark" width={20} />
                      </VerifiedBadge>
                    )}
                  </>
                )}
                {isLoaderDataFromConnection(loaderData) && (
                  <>{loaderData.connection.name}</>
                )}
              </AppName>
              {appInfo && <Body size="Large" content={appInfo.domain} />}
            </AppDetails>
          </AppSection>
          <Permissions>
            <Title content="Would like to" />
            <PermissionsList permissions={permissions} />
          </Permissions>
        </PermissionsDescription>
        <Personalize onClick={handleShowPersonalize}>
          <Title content="Personalize permissions" />
          <Icon
            name="CaretRight"
            width={12}
            iconProps={{
              strokeWidth: "2",
              strokeLinecap: "round",
              strokeLinejoin: "round",
            }}
          />
        </Personalize>
      </PermissionsContainer>

      <ButtonSection>
        <Button
          text={
            isLoaderDataFromUrl(loaderData)
              ? "Connect UMA"
              : "Update connection"
          }
          kind={isLoaderDataFromUrl(loaderData) ? "tertiary" : "primary"}
          fullWidth
          paddingY="short"
          onClick={handleSubmit}
          loading={isSubmitting}
        />
        <Button
          text="Cancel"
          kind="secondary"
          paddingY="short"
          fullWidth
          disabled={isSubmitting}
          onClick={handleBack}
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
  gap: ${Spacing.px.xs};
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
  gap: ${Spacing.px.xl};
  width: 100%;
  border-bottom: 0.5px solid #c0c9d6;
  padding: ${Spacing.px.lg};
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
`;

const AppName = styled.div`
  display: flex;
  flex-direction: row;
  gap: 4px;
`;

const VerifiedBadge = styled.div`
  color: #00d4ff;
  font-size: 12px;
`;

const Permissions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const Personalize = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 20px ${Spacing.px.lg};
  cursor: pointer;
`;

const ButtonSection = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 345px;
  width: 100%;
  gap: 16px;
`;

const ConnectYourUma = styled.span`
  font-size: 28px;
  font-weight: 400;
  line-height: 36px; /* 128.571% */
  letter-spacing: -0.35px;
`;
