export default function ConfirmModal({ message, onCancel, onConfirm }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="rounded-2xl p-6 w-80 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
        <p className="mb-5 text-sm text-slate-700 dark:text-slate-200">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
