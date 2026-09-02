import { useState, useEffect, useRef, useCallback } from "react";
import { getWhiteboardSocketUrl } from "../api/whiteboardApi";

// Owns the websocket connection for one whiteboard room: connection
// state, the live element list, who's present, and the shared variable
// memory (dictOfVars) that Run assignments write into.
export default function useWhiteboardSocket(roomId, userName) {
  const socketRef = useRef(null);
  const [elements, setElements] = useState([]);
  const [users, setUsers] = useState([]);
  const [connected, setConnected] = useState(false);
  const [dictOfVars, setDictOfVars] = useState({});

  useEffect(() => {
    const socket = new WebSocket(getWhiteboardSocketUrl(roomId, userName));
    socketRef.current = socket;

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === "init") {
        setElements(message.elements || []);
        setUsers(message.users || []);
        setDictOfVars(message.vars || {});
      } else if (message.type === "presence") {
        setUsers(message.users || []);
      } else if (message.type === "element_add" || message.type === "element_update") {
        setElements((prev) => [...prev.filter((el) => el.id !== message.element.id), message.element]);
      } else if (message.type === "element_delete") {
        setElements((prev) => prev.filter((el) => el.id !== message.element_id));
      } else if (message.type === "clear") {
        setElements([]);
      } else if (message.type === "var_update") {
        // Someone else's Run assigned a variable - fold it into our copy
        // too, so the board's memory stays shared across everyone.
        setDictOfVars((prev) => ({ ...prev, [message.name]: message.value }));
      }
    };

    return () => socket.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId, userName]);

  const send = useCallback((message) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
    }
  }, []);

  const addElementLocally = useCallback((element) => {
    setElements((prev) => [...prev.filter((el) => el.id !== element.id), element]);
  }, []);

  const clearLocally = useCallback(() => setElements([]), []);

  const setVar = useCallback(
    (name, value) => {
      setDictOfVars((prev) => ({ ...prev, [name]: value }));
      send({ type: "var_update", name, value });
    },
    [send]
  );

  return { elements, users, connected, dictOfVars, send, addElementLocally, clearLocally, setVar };
}
