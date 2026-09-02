import api from "./api";

// WebSocket URL derived from the same base as the REST API (http -> ws).
export const getWhiteboardSocketUrl = (roomId, userName) => {
  const httpBase = api.defaults.baseURL;
  const wsBase = httpBase.replace(/^http/, "ws");

  return `${wsBase}/ws/whiteboard/${encodeURIComponent(roomId)}?user_name=${encodeURIComponent(userName)}`;
};

// dictOfVars carries variables assigned in earlier Runs on this board
// (e.g. {"x": "4"}) so the backend can substitute them into later
// expressions - the board's persistent scratchpad memory.
export const solveWhiteboard = async (
  imageBase64,
  dictOfVars = {}
) => {
  const response = await api.post(
    "/whiteboard/solve",
    {
      image_base64: imageBase64,
      dict_of_vars: dictOfVars,
    }
  );

  return response.data;
};