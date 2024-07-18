import React, { useState } from "react";

export interface GlobalNotificationContextData {
  error: Error | null;
  successMessage: string | null;
  setError: (error: Error | null) => void;
  setSuccessMessage: (successMessage: string | null) => void;
  clearNotifications: () => void;
  clearErrorTimeout: () => void;
}

const Context = React.createContext<GlobalNotificationContextData>(null!);

function GlobalNotificationContextProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [data, setData] = useState<GlobalNotificationContextData>({
    error: null,
    successMessage: null,
    clearErrorTimeout: () => {},
    setError: (error) => {
      setData((prevData) => ({ ...prevData, error }));
      if (error) {
        const timeoutId = setTimeout(() => {
          setData((prevData) => ({ ...prevData, error: null }));
        }, 5000);

        setData((prevData) => ({
          ...prevData,
          clearErrorTimeout: () => clearTimeout(timeoutId),
        }));
      }
    },
    setSuccessMessage: (successMessage) => {
      setData((prevData) => ({ ...prevData, successMessage }));
      setTimeout(() => {
        setData((prevData) => ({ ...prevData, successMessage: null }));
      }, 5000);
    },
    clearNotifications: () => {
      setData((prevData) => ({
        ...prevData,
        error: null,
        successMessage: null,
      }));
    },
  });

  return <Context.Provider value={data}>{children}</Context.Provider>;
}

export function useGlobalNotificationContext() {
  return React.useContext(Context);
}

export default GlobalNotificationContextProvider;
