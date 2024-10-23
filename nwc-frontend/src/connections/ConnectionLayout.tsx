import styled from "@emotion/styled";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { Outlet } from "react-router-dom";
import { Nav } from "./Nav";

export const ConnectionLayout = () => {
  return (
    <LayoutContainer>
      <Nav />
      <Outlet />
    </LayoutContainer>
  );
};

const LayoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  gap: ${Spacing.px.xl};
`;
