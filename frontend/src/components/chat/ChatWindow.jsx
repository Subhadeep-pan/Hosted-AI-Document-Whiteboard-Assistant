import { FaRobot } from "react-icons/fa";

import MessageBubble from "./MessageBubble";
import EmptyState from "./EmptyState";
import MessageInput from "./MessageInput";

export default function ChatWindow({ messages, loading, onSend, chatEndRef }) {
  return (
    <main className="flex-1 flex flex-col bg-slate-50 dark:bg-slate-950">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            messages.map((msg, index) => (
              <MessageBubble key={index} message={msg} previousText={messages[index - 1]?.text} />
            ))
          )}

          {loading && messages[messages.length - 1]?.text === "" && (
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <FaRobot className="text-accent-500" /> Thinking...
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </div>

      <MessageInput onSend={onSend} loading={loading} />
    </main>
  );
}
