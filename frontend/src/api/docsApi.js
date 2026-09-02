import api from "./api";

export const getDocuments = async () => {
  const response = await api.get("/documents");
  return response.data.documents;
};

export const deleteDocument = async (docId) => {
  const response = await api.delete(`/documents/${docId}`);
  return response.data;
};