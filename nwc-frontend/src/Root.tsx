import { ThemeProvider } from "@emotion/react";
import styled from "@emotion/styled";
import { themes } from "@lightsparkdev/ui/styles/themes";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import GlobalNotificationContext from "src/hooks/useGlobalNotificationContext";
import App from "./App";
import { ConnectionLayout } from "./connections/ConnectionLayout";
import ConnectionPage from "./connections/ConnectionPage";
import ManualConnectionPage from "./connections/ManualConnectionPage";
import { GlobalStyles } from "./GlobalStyles";
import { LayoutInnerContent } from "./LayoutInnerContent";
import { permissionsPageData } from "./loaders/permissionPageData";
import { permissionsPageDataFromUrl } from "./loaders/permissionPageDataFromUrl";
import { userCurrencies } from "./loaders/userCurrencies";
import { Nav } from "./Nav";
import { NotificationLayout } from "./NotificationLayout";
import { PermissionsPage } from "./permissions/PermissionsPage";
import { useAuth } from "./utils/auth";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  {
    element: <ConnectionLayout />,
    path: "/connection",
    children: [
      {
        path: ":connectionId",
        element: <ConnectionPage />,
      },
      {
        path: "new",
        element: <ManualConnectionPage />,
        loader: userCurrencies,
      },
      {
        path: "update/:connectionId",
        element: <PermissionsPage />,
        loader: permissionsPageData,
      },
    ],
  },
  {
    path: "/apps/new",
    element: <PermissionsPage />,
    loader: permissionsPageDataFromUrl,
  },
]);

export function Root() {
  const auth = useAuth();
  if (!auth.isLoggedIn()) {
    auth.redirectToLogin();
    return null;
  }

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
  overflow: scroll;

  display: flex;
  flex-direction: column;
`;
