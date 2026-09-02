import api from "./api";

export const getSummary = async (
    docId
) => {

    const response =
        await api.get(
            "/summary",
            {
                params: {
                    doc_id: docId
                }
            }
        );

    return response.data;
};