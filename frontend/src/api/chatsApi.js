import api from "./api";

export const getChats = async () => {
  const response = await api.get("/chats");
  return response.data.chats;
};

export const createChat = async () => {
  const response = await api.post("/chats");
  return response.data.chat_id;
};

export const deleteChat = async (chatId) => {
  const response = await api.delete(`/chats/${chatId}`);
  return response.data;
};

export const renameChat = async (chatId, title) => {
  const response = await api.patch(`/chats/${chatId}`, { title });
  return response.data;
};