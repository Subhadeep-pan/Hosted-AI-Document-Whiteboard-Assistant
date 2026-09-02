import { FaRobot } from "react-icons/fa";
import MessageMeta from "./MessageMeta";

export default function MessageBubble({ message, previousText }) {
  const isUser = message.role === "User";

  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-1.5 text-sm font-medium">
        {isUser ? (
          "You"
        ) : (
          <>
            <span className="w-6 h-6 rounded-full bg-accent-100 dark:bg-accent-700/30 text-accent-600 dark:text-accent-200 flex items-center justify-center">
              <FaRobot size={11} />
            </span>
            Assistant
          </>
        )}
      </div>

      <div className="whitespace-pre-wrap leading-relaxed text-[15px] text-slate-800 dark:text-slate-100">
        {message.text}
      </div>

      {!isUser && message.meta && (
        <MessageMeta question={previousText} answer={message.text} meta={message.meta} />
      )}
    </div>
  );
}
