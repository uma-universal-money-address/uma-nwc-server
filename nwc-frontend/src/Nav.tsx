import styled from "@emotion/styled";
import { UnstyledButton } from "@lightsparkdev/ui/components";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { Uma } from "src/components/Uma";
import { getAuth } from "./utils/auth";
import { getConfig } from "./utils/getConfig";

export const Nav = () => {
  const auth = getAuth();
  const uma = auth.getUmaAddress();
  const { vaspName, vaspLogoUrl } = getConfig();

  return (
    <NavContainer>
      <NavLeftSide>
        <img
          alt={vaspName}
          src={vaspLogoUrl || "/vasp.svg"}
          width={24}
          height={24}
        />
        <Divider />
        <Name>UMA Connections</Name>
      </NavLeftSide>
      <NavRightSide>
        <Uma uma={uma} />
        <LogOutButton onClick={() => auth.logout()}>Log out</LogOutButton>
      </NavRightSide>
    </NavContainer>
  );
};

const NavContainer = styled.section`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 100%;
  align-items: center;
  padding: ${Spacing.md} ${Spacing.xl};
  border-bottom: 1px solid #dedfe4;
  gap: ${Spacing.md};
`;

const NavLeftSide = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: ${Spacing.sm};
`;

const NavRightSide = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: ${Spacing.xl};
`;

const LogOutButton = styled(UnstyledButton)`
  color: #777;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  line-height: 24px; /* 171.429% */
  width: 100%;
`;

const Divider = styled.div`
  height: 20px;
  width: 1px;
  background: ${colors.grayBlue80};
`;

const Name = styled.span`
  color: #000;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
  white-space: nowrap;
`;
