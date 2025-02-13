let cachedConfig: {
  vaspLoginUrl: URL;
  vaspName: string;
  vaspLogoUrl: string;
  basePath: string;
} | null = null;

const fetchFromMeta = (name: string, required: boolean): string => {
  const meta = document.querySelector(`meta[name="${name}"]`);
  if (!meta) {
    if (required) {
      throw new Error(`Config value ${name} is not defined.`);
    }
    return "";
  }
  return meta.getAttribute("content") || "";
};

export function getConfig() {
  if (cachedConfig) {
    return cachedConfig;
  }

  const loginUrlString = fetchFromMeta("uma-vasp-login-url", true);
  if (!URL.canParse(loginUrlString)) {
    throw new Error("Invalid UMA_VASP_LOGIN_URL");
  }
  const vaspLoginUrl = new URL(loginUrlString);

  let basePath = fetchFromMeta("base-path", false);
  if (basePath !== "") {
    basePath = "/" + basePath.replace(/^\/+|\/+$/, "");
  }

  cachedConfig = {
    vaspLoginUrl: vaspLoginUrl,
    vaspName: fetchFromMeta("vasp-name", true),
    vaspLogoUrl: fetchFromMeta("vasp-logo-url", true),
    basePath: basePath,
  };
  return cachedConfig;
}
