import api from "./api";

export const getChatHistory = async (chatId) => {
  const response = await api.get("/history", {
    params: { chat_id: chatId },
  });

  return response.data;
};
