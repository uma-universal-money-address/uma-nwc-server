import { useConfig } from "src/hooks/useConfig";
import { getBackendUrl } from "./backendUrl";

type LoginState = {
  umaAddress: string;
  authToken: string;
  validUntil: string;
};

let globalLoginState: LoginState | null = null;

export class Auth {
  private redirectingToLogin = false;
  private vaspLoginUrl: URL;

  constructor(vaspLoginUrl: URL) {
    this.vaspLoginUrl = vaspLoginUrl;
    this.handleToken();
  }

  handleToken() {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      globalLoginState = {
        umaAddress: params.get("uma_address") || "",
        authToken: token,
        validUntil: params.get("valid_until") || "",
      };
      const url = new URL(window.location.href);
      url.searchParams.delete("token");
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
    if (new Date(globalLoginState.validUntil) < new Date()) {
      this.logout();
      return false;
    }
    return true;
  }
}

export const useAuth = () => {
  const { vaspLoginUrl } = useConfig();
  const auth = new Auth(vaspLoginUrl);
  return auth;
};
