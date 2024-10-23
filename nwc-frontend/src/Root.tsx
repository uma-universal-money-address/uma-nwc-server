import { ThemeProvider } from "@emotion/react";
import styled from "@emotion/styled";
import { themes } from "@lightsparkdev/ui/styles/themes";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import App from "./App";
import { AppLayout } from "./AppLayout";
import { ConnectionLayout } from "./connections/ConnectionLayout";
import ConnectionPage from "./connections/ConnectionPage";
import ManualConnectionPage from "./connections/ManualConnectionPage";
import { GlobalStyles } from "./GlobalStyles";
import { permissionsPageData } from "./loaders/permissionPageData";
import { permissionsPageDataFromUrl } from "./loaders/permissionPageDataFromUrl";
import { PermissionsPage } from "./permissions/PermissionsPage";
import { PermissionsLayout } from "./PermissionsLayout";
import { getAuth } from "./utils/auth";

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
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
          },
        ],
      },
    ],
  },
  {
    element: <PermissionsLayout />,
    children: [
      {
        path: "/apps/new",
        element: <PermissionsPage />,
        loader: permissionsPageDataFromUrl,
      },
      {
        path: "/connection/:connectionId/update",
        element: <PermissionsPage />,
        loader: permissionsPageData,
      },
    ],
  },
]);

export function Root() {
  const auth = getAuth();
  if (!auth.isLoggedIn()) {
    auth.redirectToLogin();
    return null;
  }

  return (
    <ThemeProvider theme={themes.umaAuthSdkLight}>
      <GlobalStyles />
      <Container>
        <RouterProvider router={router} />
      </Container>
    </ThemeProvider>
  );
}

const Container = styled.div`
  width: 100%;
  height: 100vh;
`;
