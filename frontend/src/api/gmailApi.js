import api from "./api";

export const getGmailStatus = async () => {
  const response = await api.get("/auth/gmail/status");
  return response.data.connected;
};

export const getGmailConnectUrl = async () => {
  const response = await api.get("/auth/gmail/connect");
  return response.data.auth_url;
};

export const disconnectGmail = async () => {
  const response = await api.post("/auth/gmail/disconnect");
  return response.data;
};
