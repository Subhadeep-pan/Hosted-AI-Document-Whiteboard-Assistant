import { FaComment, FaPen, FaTrash } from "react-icons/fa";

// Groups chats into ChatGPT/Claude-style date buckets so the sidebar
// stays scannable as the list grows, instead of one long flat list.
function groupByDate(chats) {
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);
  const sevenDaysAgo = new Date(startOfToday);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const groups = { Today: [], Yesterday: [], "Previous 7 Days": [], Older: [] };

  for (const chat of chats) {
    const createdAt = new Date(chat.created_at * 1000);

    if (createdAt >= startOfToday) groups.Today.push(chat);
    else if (createdAt >= startOfYesterday) groups.Yesterday.push(chat);
    else if (createdAt >= sevenDaysAgo) groups["Previous 7 Days"].push(chat);
    else groups.Older.push(chat);
  }

  return Object.entries(groups).filter(([, items]) => items.length > 0);
}

export default function ChatList({ chats, currentChatId, onOpen, onRename, onDelete }) {
  if (chats.length === 0) {
    return <p className="text-sm text-slate-400 px-1">No chats yet.</p>;
  }

  const groups = groupByDate(chats);

  return (
    <div className="space-y-3">
      {groups.map(([label, items]) => (
        <div key={label}>
          <h3 className="text-[11px] font-medium uppercase tracking-wide text-slate-400 px-3 mb-1">{label}</h3>
          <ul className="space-y-0.5">
            {items.map((chat) => {
              const active = chat.chat_id === currentChatId;

              return (
                <li
                  key={chat.chat_id}
                  onClick={() => onOpen(chat.chat_id)}
                  className={`group flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${
                    active
                      ? "bg-accent-100 dark:bg-accent-700/30 text-accent-700 dark:text-accent-100"
                      : "hover:bg-slate-100 dark:hover:bg-slate-800/60"
                  }`}
                >
                  <span className="flex items-center gap-2 truncate">
                    <FaComment className="shrink-0 opacity-50" size={12} />
                    <span className="truncate">{chat.title}</span>
                  </span>

                  <span className="opacity-0 group-hover:opacity-100 flex items-center gap-2 shrink-0 transition-opacity">
                    <button
                      onClick={(e) => onRename(chat, e)}
                      className="text-slate-400 hover:text-accent-600 transition-colors"
                      title="Rename chat"
                    >
                      <FaPen size={11} />
                    </button>
                    <button
                      onClick={(e) => onDelete(chat.chat_id, e)}
                      className="text-slate-400 hover:text-red-500 transition-colors"
                      title="Delete chat"
                    >
                      <FaTrash size={11} />
                    </button>
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </div>
  );
}
