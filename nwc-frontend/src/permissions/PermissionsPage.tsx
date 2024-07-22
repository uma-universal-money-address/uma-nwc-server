import styled from "@emotion/styled";
import { Button, Icon, UnstyledButton } from "@lightsparkdev/ui/components";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Avatar } from "src/components/Avatar";
import { Uma } from "src/components/Uma";
import { useConnection } from "src/hooks/useConnection";
import { useUma } from "src/hooks/useUma";
import { LimitFrequency } from "src/types/Connection";
import { convertToNormalDenomination } from "src/utils/convertToNormalDenomination";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { EditLimit } from "./EditLimit";
import { PermissionsList } from "./PermissionsList";


export const PermissionsPage = ({ appId }: { appId: string }) => {
  const { connection, updateConnection, isLoading: isLoadingConnection } = useConnection({ appId });
  const { uma, isLoading: isLoadingUma } = useUma();

  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);

  if (isLoadingConnection || isLoadingUma) {
    return (
      <Container>
        <Title content="Loading..." />
      </Container>
    )
  }

  const { 
    name,
    domain,
    createdAt,
    lastUsed,
    avatar,
    permissions,
    amountInLowestDenom,
    limitFrequency,
    limitEnabled,
    currency,
    verified,
  } = connection;

  const handleEdit = () => {
    setIsEditLimitVisible(true);
  }

  const handleSubmitEditLimit = ({ amountInLowestDenom, frequency, enabled }: {amountInLowestDenom: number, frequency: LimitFrequency, enabled: boolean}) => {
    updateConnection({ amountInLowestDenom, limitFrequency: frequency, limitEnabled: enabled });
    setIsEditLimitVisible(false);
  }

  const header = (
    <Header>
      <VaspLogo src="/vasp.svg" width={32} height={32} />
      <UnstyledButton>
        <Icon name="Close" width={8} />
      </UnstyledButton>
    </Header>
  )
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
                {verified ? (<VerifiedBadge>
                  <Icon name="CheckmarkCircleTier3" width={20}/>
                </VerifiedBadge>) : null}
              </AppName>
              <AppDomain>{domain}</AppDomain>
            </AppDetails>
          </AppSection>
          <Permissions>
            <Label size="Large" content="Would like to" />
            <PermissionsList permissions={permissions} />
          </Permissions>
        </PermissionsDescription>
        <Limit onClick={handleEdit}>
          <LimitDescription>{
            limitEnabled ? `${formatConnectionString({ currency, limitFrequency, amountInLowestDenom })} spending limit` : "No spending limit"
          }</LimitDescription>
          <Icon name="Pencil" width={12} />
        </Limit>
      </PermissionsContainer>

      <ButtonSection>
        <Button text="Connect UMA" kind="primary" fullWidth />
        <Button text="Cancel" kind="secondary" fullWidth />
      </ButtonSection>

      <EditLimit
        visible={isEditLimitVisible}
        amountInLowestDenom={amountInLowestDenom}
        currency={currency}
        limitFrequency={limitFrequency}
        frequency={limitFrequency}
        enabled={limitEnabled}
        handleSubmit={handleSubmitEditLimit}
        handleCancel={() => setIsEditLimitVisible(false)}
      />
    </Container>
  )
}

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

const VaspLogo = styled.img`
`;

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
  border: 0.5px solid #C0C9D6;
  border-radius: 8px;
`;

const PermissionsDescription = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xl};
  width: 100%;
  border-bottom: 0.5px solid #C0C9D6;
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

const Limit = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: ${Spacing.lg};
  cursor: pointer;
`;

const LimitDescription = styled.div`
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