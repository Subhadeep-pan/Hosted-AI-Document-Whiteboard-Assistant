import { useState, useEffect, useRef } from "react";
import { askQuestionStream } from "../api/chatApi";
import { getChatHistory } from "../api/historyApi";

// Owns the message list for whichever chat is currently open, and the
// streaming send flow. Reloads automatically whenever chatId changes.
export default function useChatSession(chatId, onAnswered) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (!chatId) return;

    (async () => {
      const data = await getChatHistory(chatId).catch(() => ({ history: [] }));
      setMessages(data.history || []);
    })();
  }, [chatId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const appendAssistantChunk = (chunk) => {
    setMessages((prev) => {
      const updated = [...prev];
      const lastIndex = updated.length - 1;
      updated[lastIndex] = { ...updated[lastIndex], text: updated[lastIndex].text + chunk };
      return updated;
    });
  };

  const attachMeta = (meta) => {
    setMessages((prev) => {
      const updated = [...prev];
      const lastIndex = updated.length - 1;
      updated[lastIndex] = { ...updated[lastIndex], meta };
      return updated;
    });
  };

  const send = async (question) => {
    if (!question.trim() || loading || !chatId) return;

    setMessages((prev) => [...prev, { role: "User", text: question }, { role: "Assistant", text: "" }]);
    setLoading(true);

    try {
      await askQuestionStream(question, chatId, appendAssistantChunk, attachMeta);
      onAnswered?.();
      // The chat title (for a brand-new chat) is generated in a
      // background thread on the backend now, so it isn't guaranteed to
      // be ready the instant streaming ends. One extra refresh shortly
      // after picks it up without polling indefinitely.
      setTimeout(() => onAnswered?.(), 1500);
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "Assistant", text: "Error connecting to the backend." };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const appendMessage = (role, text) => setMessages((prev) => [...prev, { role, text }]);

  return { messages, loading, send, appendMessage, chatEndRef };
}
