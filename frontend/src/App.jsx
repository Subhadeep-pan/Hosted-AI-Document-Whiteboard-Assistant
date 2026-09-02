import { useState, useEffect } from "react";

import useChats from "./hooks/useChats";
import useChatSession from "./hooks/useChatSession";
import useDocuments from "./hooks/useDocuments";

import { getSummary } from "./api/summaryApi";

import Sidebar from "./components/sidebar/Sidebar";
import ChatWindow from "./components/chat/ChatWindow";
import ConfirmModal from "./components/modals/ConfirmModal";
import RenameModal from "./components/modals/RenameModal";
import RoomJoin from "./components/whiteboard/RoomJoin";
import Whiteboard from "./components/whiteboard/Whiteboard";

function App() {
  const [darkMode, setDarkMode] = useState(localStorage.getItem("theme") === "dark");

  // Tailwind v4 has no config file - dark: utilities respond to a
  // ".dark" ancestor class (see the @custom-variant in index.css), so
  // toggling it on <html> makes dark mode apply everywhere, including
  // the whiteboard/room-join screens that render outside the main
  // wrapper div below.
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);
  const [view, setView] = useState("chat"); // "chat" | "room-join" | "whiteboard"
  const [whiteboardRoom, setWhiteboardRoom] = useState(null);
  const [confirmState, setConfirmState] = useState(null); // { message, onConfirm }
  const [renameState, setRenameState] = useState(null); // { chat }

  const toggleDarkMode = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  const { chats, currentChatId, selectChat, newChat, removeChat, rename, refreshTitles } = useChats();
  const { messages, loading, send, appendMessage, chatEndRef } = useChatSession(currentChatId, refreshTitles);
  const { documents, uploadMessage, upload, remove: removeDocument, resetAll } = useDocuments();

  const handleNewChat = () => newChat(messages.length === 0);

  const handleDeleteChat = (chatId, event) => {
    event.stopPropagation();
    setConfirmState({
      message: "Delete this chat? This cannot be undone.",
      onConfirm: () => removeChat(chatId),
    });
  };

  const handleRenameChat = (chat, event) => {
    event.stopPropagation();
    setRenameState({ chat });
  };

  const handleDeleteDocument = (docId, event) => {
    event.stopPropagation();
    setConfirmState({
      message: `Delete "${docId}"? This cannot be undone.`,
      onConfirm: () => removeDocument(docId),
    });
  };

  const handleSummarize = async (docId) => {
    appendMessage("User", `Summarize ${docId}`);
    try {
      const result = await getSummary(docId);
      appendMessage("Assistant", result.summary);
    } catch {
      appendMessage("Assistant", "Failed to load summary.");
    }
  };

  if (view === "room-join") {
    return (
      <RoomJoin
        onJoin={(roomId, userName) => {
          setWhiteboardRoom({ roomId, userName });
          setView("whiteboard");
        }}
      />
    );
  }

  if (view === "whiteboard" && whiteboardRoom) {
    return (
      <Whiteboard
        roomId={whiteboardRoom.roomId}
        userName={whiteboardRoom.userName}
        darkMode={darkMode}
        onLeave={() => setView("chat")}
      />
    );
  }

  return (
    <div className="flex h-screen">
      <Sidebar
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
        chats={chats}
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onOpenChat={selectChat}
        onRenameChat={handleRenameChat}
        onDeleteChat={handleDeleteChat}
        documents={documents}
        uploadMessage={uploadMessage}
        onUpload={upload}
        onDeleteDocument={handleDeleteDocument}
        onSummarize={handleSummarize}
        onResetDocuments={resetAll}
        onOpenWhiteboard={() => setView("room-join")}
      />

      <ChatWindow messages={messages} loading={loading} onSend={send} chatEndRef={chatEndRef} />

      {confirmState && (
        <ConfirmModal
          message={confirmState.message}
          onCancel={() => setConfirmState(null)}
          onConfirm={() => {
            confirmState.onConfirm();
            setConfirmState(null);
          }}
        />
      )}

      {renameState && (
        <RenameModal
          initialValue={renameState.chat.title}
          onCancel={() => setRenameState(null)}
          onSave={(value) => {
            if (value.trim()) rename(renameState.chat.chat_id, value.trim());
            setRenameState(null);
          }}
        />
      )}
    </div>
  );
}

export default App;
