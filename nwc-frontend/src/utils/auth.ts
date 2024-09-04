import { useConfig } from "src/hooks/useConfig";
import { getBackendUrl } from "./backendUrl";

type LoginState = {
  umaAddress: string;
  authToken: string;
  validUntil: Date | null;
};

let globalLoginState: LoginState | null = null;

export class Auth {
  private redirectingToLogin = false;
  private vaspLoginUrl: URL;

  constructor(vaspLoginUrl: URL) {
    this.vaspLoginUrl = vaspLoginUrl;
    this.handleToken();
  }

  private handleToken() {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      const expiryStr = params.get("expiry");
      const expiry = expiryStr ? new Date(parseFloat(expiryStr) * 1000) : null;
      globalLoginState = {
        umaAddress: params.get("uma_address") || "",
        authToken: token,
        validUntil: expiry,
      };
      const url = new URL(window.location.href);
      url.searchParams.delete("token");
      url.searchParams.delete("expiry");
      url.searchParams.delete("uma_address");
      window.history.replaceState({}, document.title, url.toString());
    }
  }

  redirectToLogin() {
    if (this.redirectingToLogin) return;
    this.redirectingToLogin = true;
    const currentPath = window.location.pathname;
    const currentQueryParams = window.location.search;
    const frontendRedirectUrl = `${currentPath}${currentQueryParams}`;
    const backendRedirect = `${getBackendUrl()}/auth/vasp_token_callback?fe_redirect=${encodeURIComponent(frontendRedirectUrl)}`;

    const loginRedirectUrlParams = this.vaspLoginUrl.searchParams;
    loginRedirectUrlParams.set(
      "redirect_uri",
      encodeURIComponent(backendRedirect),
    );
    console.log("Redirecting to login", this.vaspLoginUrl.toString());
    window.location.href = this.vaspLoginUrl.toString();
  }

  logout() {
    globalLoginState = null;
    this.redirectToLogin();
  }

  isLoggedIn() {
    if (!globalLoginState) {
      return false;
    }
    if (
      !globalLoginState.validUntil ||
      globalLoginState.validUntil < new Date()
    ) {
      this.logout();
      return false;
    }
    return true;
  }

  getAuthToken() {
    if (!this.isLoggedIn()) {
      return null;
    }
    return globalLoginState?.authToken;
  }

  getUmaAddress() {
    if (!this.isLoggedIn()) {
      return null;
    }
    return globalLoginState?.umaAddress;
  }
}

export const useAuth = () => {
  const { vaspLoginUrl } = useConfig();
  const auth = new Auth(vaspLoginUrl);
  return auth;
};
