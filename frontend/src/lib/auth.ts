export const AUTH_COOKIE_NAME = "pm_auth";
export const AUTH_COOKIE_VALUE = "1";
export const DUMMY_USERNAME = "user";
export const DUMMY_PASSWORD = "password";

export const validateCredentials = (username: string, password: string): boolean => {
  return username.trim() === DUMMY_USERNAME && password === DUMMY_PASSWORD;
};

export const hasAuthCookie = (cookieHeader: string): boolean => {
  return cookieHeader
    .split(";")
    .map((part) => part.trim())
    .includes(`${AUTH_COOKIE_NAME}=${AUTH_COOKIE_VALUE}`);
};

export const buildAuthCookie = (): string => {
  return `${AUTH_COOKIE_NAME}=${AUTH_COOKIE_VALUE}; Path=/; SameSite=Lax`;
};

export const buildClearAuthCookie = (): string => {
  return `${AUTH_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`;
};
