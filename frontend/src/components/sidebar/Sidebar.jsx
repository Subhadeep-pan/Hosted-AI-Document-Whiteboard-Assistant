import { FaPlus, FaChalkboard, FaMoon, FaSun } from "react-icons/fa";

import ChatList from "./ChatList";
import DocumentPanel from "./DocumentPanel";
import GmailConnect from "../gmail/GmailConnect";

export default function Sidebar({
  darkMode,
  onToggleDarkMode,
  chats,
  currentChatId,
  onNewChat,
  onOpenChat,
  onRenameChat,
  onDeleteChat,
  documents,
  uploadMessage,
  onUpload,
  onDeleteDocument,
  onSummarize,
  onResetDocuments,
  onOpenWhiteboard,
}) {
  return (
    <aside className="w-72 flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-base font-semibold">AI resume assistant</h1>
        <button
          onClick={onToggleDarkMode}
          className="w-8 h-8 flex items-center justify-center rounded-full text-slate-400 hover:text-accent-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={darkMode ? "Light mode" : "Dark mode"}
        >
          {darkMode ? <FaSun size={14} /> : <FaMoon size={14} />}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 justify-center py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
        >
          <FaPlus size={12} /> New chat
        </button>

        <button
          onClick={onOpenWhiteboard}
          className="flex items-center gap-2 justify-center py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
        >
          <FaChalkboard size={12} /> Board
        </button>
      </div>

      <GmailConnect />

      <h2 className="text-xs font-medium uppercase tracking-wide text-slate-400 mb-1.5 mt-1">Chats</h2>
      <div className="flex-1 min-h-[6rem] overflow-y-auto mb-4">
        <ChatList
          chats={chats}
          currentChatId={currentChatId}
          onOpen={onOpenChat}
          onRename={onRenameChat}
          onDelete={onDeleteChat}
        />
      </div>

      <DocumentPanel
        documents={documents}
        uploadMessage={uploadMessage}
        onUpload={onUpload}
        onDelete={onDeleteDocument}
        onSummarize={onSummarize}
        onReset={onResetDocuments}
      />
    </aside>
  );
}
