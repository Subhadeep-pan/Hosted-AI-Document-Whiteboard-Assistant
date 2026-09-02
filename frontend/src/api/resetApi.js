import api from "./api";

export const resetProject = async () => {

    const response =
        await api.delete(
            "/reset"
        );

    return response.data;
};
