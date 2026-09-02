import api from "./api";

export const uploadFile = async (
    files
) => {

    const formData =
        new FormData();

    files.forEach(
        (file) => {

            formData.append(
                "files",
                file
            );

        }
    );

    const response =
        await api.post(
            "/upload",
            formData,
            {
                headers: {
                    "Content-Type":
                        "multipart/form-data"
                }
            }
        );

    return response.data;
};