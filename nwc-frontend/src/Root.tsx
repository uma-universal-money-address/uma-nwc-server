import { ThemeProvider } from "@emotion/react";
import styled from "@emotion/styled";
import { themes } from "@lightsparkdev/ui/styles/themes";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import GlobalNotificationContext from "src/hooks/useGlobalNotificationContext";
import App from "./App";
import ConnectionPage from "./connections/ConnectionPage";
import ManualConnectionPage from "./connections/ManualConnectionPage";
import { GlobalStyles } from "./GlobalStyles";
import { LayoutInnerContent } from "./LayoutInnerContent";
import { Nav } from "./Nav";
import { NotificationLayout } from "./NotificationLayout";
import { PermissionsPage } from "./permissions/PermissionsPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    path: "/connection/:appId",
    element: <ConnectionPage />,
  },
  {
    path: "/connection/new",
    element: <ManualConnectionPage />,
  },
  {
    path: "/permissions/:appId",
    element: <PermissionsPage />,
  },
]);

export function Root() {
  return (
    <ThemeProvider theme={themes.umameDocsLight}>
      <GlobalStyles />
      <Container>
        <InnerContainer>
          <GlobalNotificationContext>
            <NotificationLayout>
              <Nav />
              <LayoutInnerContent>
                <RouterProvider router={router} />
              </LayoutInnerContent>
            </NotificationLayout>
          </GlobalNotificationContext>
        </InnerContainer>
      </Container>
    </ThemeProvider>
  );
}

const Container = styled.div`
  width: 100%;
  height: 100vh;
  background-color: ${({ theme }) => theme.bg};
`;

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

  display: flex;
  flex-direction: column;
`;
