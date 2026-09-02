import api from "./api";

export const sendFeedback = async (question, answer, helpful) => {
  const response = await api.post("/feedback", { question, answer, helpful });
  return response.data;
};
