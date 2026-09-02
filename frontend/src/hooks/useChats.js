import { useState, useEffect } from "react";
import { getChats, createChat, deleteChat, renameChat } from "../api/chatsApi";

const LAST_CHAT_KEY = "last_chat_id";

// Owns the chat list (sidebar) and which chat is currently open.
// Message content for the open chat lives in useChatSession, not here.
export default function useChats() {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

  const selectChat = (chatId) => {
    setCurrentChatId(chatId);
    localStorage.setItem(LAST_CHAT_KEY, chatId);
  };

  useEffect(() => {
    (async () => {
      const existingChats = await getChats().catch(() => []);

      if (existingChats.length === 0) {
        const chatId = await createChat();
        setChats([{ chat_id: chatId, title: "New Chat", created_at: Date.now() / 1000 }]);
        selectChat(chatId);
        return;
      }

      setChats(existingChats);

      const lastChatId = localStorage.getItem(LAST_CHAT_KEY);
      const stillExists = existingChats.some((chat) => chat.chat_id === lastChatId);

      selectChat(stillExists ? lastChatId : existingChats[0].chat_id);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const refreshTitles = async () => {
    const fresh = await getChats().catch(() => null);
    if (fresh) setChats(fresh);
  };

  const newChat = async (currentChatIsEmpty) => {
    if (currentChatId && currentChatIsEmpty) return currentChatId;

    const chatId = await createChat();
    setChats((prev) => [{ chat_id: chatId, title: "New Chat", created_at: Date.now() / 1000 }, ...prev]);
    selectChat(chatId);
    return chatId;
  };

  const removeChat = async (chatId) => {
    await deleteChat(chatId);
    const remaining = chats.filter((chat) => chat.chat_id !== chatId);
    setChats(remaining);

    if (chatId !== currentChatId) return;

    if (remaining.length > 0) {
      selectChat(remaining[0].chat_id);
    } else {
      newChat(false);
    }
  };

  const rename = async (chatId, newTitle) => {
    await renameChat(chatId, newTitle);
    setChats((prev) => prev.map((c) => (c.chat_id === chatId ? { ...c, title: newTitle } : c)));
  };

  return { chats, currentChatId, selectChat, newChat, removeChat, rename, refreshTitles };
}
