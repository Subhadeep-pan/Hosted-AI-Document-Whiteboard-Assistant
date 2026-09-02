import { FaTrash, FaPlay } from "react-icons/fa";

const COLORS = [
  "#1f2937",
  "#dc2626",
  "#2563eb",
  "#16a34a",
  "#d97706",
];

export default function WhiteboardToolbar({
  color,
  onColorChange,
  onClear,
  onRun,
  running,
  runError,
  dictOfVars,
}) {
  const varEntries = Object.entries(
    dictOfVars || {}
  );

  return (
    <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-2.5">

      <div className="flex items-center gap-1.5">
        {COLORS.map((c) => (
          <button
            key={c}
            onClick={() => onColorChange(c)}
            className={`w-6 h-6 rounded-full border-2 transition-transform ${
              color === c
                ? "border-accent-500 scale-110"
                : "border-transparent"
            }`}
            style={{
              backgroundColor: c,
            }}
            title={c}
          />
        ))}
      </div>


      <button
        onClick={onClear}
        className="ml-2 flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
      >
        <FaTrash size={11} />
        Clear board
      </button>


      <button
        onClick={onRun}
        disabled={running}
        className="flex items-center gap-2 text-sm px-4 py-1.5 rounded-lg bg-accent-600 hover:bg-accent-700 disabled:opacity-50 text-white font-medium transition-colors"
      >
        <FaPlay size={10} />

        {running
          ? "Running..."
          : "Run"}
      </button>


      {runError && (
        <span className="text-xs text-red-500">
          {runError}
        </span>
      )}


      {varEntries.length > 0 && (
        <div className="ml-auto flex items-center gap-1.5 text-xs text-slate-400 overflow-hidden">

          <span className="shrink-0">
            Memory:
          </span>

          {varEntries.map(
            ([name, value]) => (
              <span
                key={name}
                className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 font-mono shrink-0"
              >
                {name}={value}
              </span>
            )
          )}

        </div>
      )}

    </div>
  );
}