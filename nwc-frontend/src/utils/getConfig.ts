declare global {
  interface Window {
    NWC_CONFIG: {
      UMA_VASP_LOGIN_URL: string;
      VASP_NAME: string;
      VASP_LOGO_URL: string;
    };
  }
}

export function getConfig() {
  const config = (window as Window).NWC_CONFIG;
  if (!config) {
    throw new Error("NWC_CONFIG is not defined.");
  }
  const assertDefinedAndNotEmpty = (key: string): string => {
    const configAsMap = config as Record<string, string>;
    if (configAsMap[key] === undefined || configAsMap[key] === "") {
      throw new Error(`${key} is not defined.`);
    }
    if (typeof configAsMap[key] !== "string") {
      throw new Error(`${key} is not a string.`);
    }
    return configAsMap[key];
  };

  const loginUrlString = assertDefinedAndNotEmpty("UMA_VASP_LOGIN_URL");
  if (!URL.canParse(loginUrlString)) {
    throw new Error("Invalid UMA_VASP_LOGIN_URL");
  }
  const vaspLoginUrl = new URL(loginUrlString);
  return {
    vaspLoginUrl: vaspLoginUrl,
    vaspName: assertDefinedAndNotEmpty("VASP_NAME"),
    vaspLogoUrl: assertDefinedAndNotEmpty("VASP_LOGO_URL"),
  };
}
