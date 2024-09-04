import styled from "@emotion/styled";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { Uma } from "src/components/Uma";
import { useAuth } from "./utils/auth";

export const Nav = () => {
  const auth = useAuth();
  const uma = auth.getUmaAddress();

  return (
    <NavContainer>
      <NavLeftSide>
        <img alt="Exchange" src="/vasp.svg" width={24} height={24} />
        <Divider />
        <Name>UMA Connections</Name>
      </NavLeftSide>
      <a href="/vasp">
        <Uma uma={uma} />
      </a>
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
