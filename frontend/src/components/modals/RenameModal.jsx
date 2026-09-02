import { useState } from "react";

export default function RenameModal({ initialValue, onCancel, onSave }) {
  const [value, setValue] = useState(initialValue);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="rounded-2xl p-6 w-80 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <p className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-200">Rename chat</p>
        <input
          autoFocus
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSave(value)}
          className="w-full rounded-lg px-3 py-2 mb-4 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 outline-none focus:ring-2 focus:ring-accent-500"
        />
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(value)}
            className="px-4 py-2 text-sm rounded-lg bg-accent-600 hover:bg-accent-700 text-white transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
