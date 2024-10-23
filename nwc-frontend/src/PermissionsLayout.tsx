import styled from "@emotion/styled";
import { Outlet } from "react-router-dom";
import { LayoutInnerContent } from "./LayoutInnerContent";

export const PermissionsLayout = () => {
  return (
    <>
      <InnerContainer>
        <LayoutInnerContent>
          <Outlet />
        </LayoutInnerContent>
      </InnerContainer>
    </>
  );
};

const InnerContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  height: calc(100% - env(safe-area-inset-top));
  width: 100vw;
  padding-top: env(safe-area-inset-top);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safecare-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  overflow: scroll;
  background-color: white;
  min-width: 320px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;
