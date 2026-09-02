import { useState } from "react";
import { FaPaperPlane } from "react-icons/fa";

export default function MessageInput({ onSend, loading }) {
  const [value, setValue] = useState("");

  const submit = () => {
    if (!value.trim()) return;
    onSend(value);
    setValue("");
  };

  return (
    <div className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div className="max-w-3xl mx-auto flex gap-3">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Ask a question about your documents..."
          className="flex-1 rounded-2xl px-4 py-3 outline-none focus:ring-2 focus:ring-accent-500 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 placeholder:text-slate-400"
        />
        <button
          onClick={submit}
          disabled={loading}
          className="flex items-center gap-2 bg-accent-600 hover:bg-accent-700 disabled:opacity-50 text-white px-6 rounded-2xl font-medium transition-colors"
        >
          <FaPaperPlane size={13} /> Send
        </button>
      </div>
    </div>
  );
}
