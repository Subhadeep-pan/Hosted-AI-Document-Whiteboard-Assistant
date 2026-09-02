import { FaArrowLeft, FaCircle } from "react-icons/fa";

const AVATAR_COLORS = [
  "#7F77DD",
  "#1D9E75",
  "#D85A30",
  "#D4537E",
  "#378ADD",
];

function colorFor(name) {
  let hash = 0;

  for (let i = 0; i < name.length; i++) {
    hash =
      name.charCodeAt(i) +
      ((hash << 5) - hash);
  }

  return AVATAR_COLORS[
    Math.abs(hash) % AVATAR_COLORS.length
  ];
}

export default function WhiteboardTopBar({
  roomId,
  connected,
  users,
  onLeave,
}) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3">

      <div className="flex items-center gap-4">

        <button
          onClick={onLeave}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-accent-600 transition-colors"
        >
          <FaArrowLeft size={12} />
          Back to chat
        </button>


        <span className="text-sm font-semibold">
          Room: {roomId}
        </span>


        <span
          className={`text-xs flex items-center gap-1.5 ${
            connected
              ? "text-green-500"
              : "text-amber-500"
          }`}
        >
          <FaCircle size={7} />

          {connected
            ? "Connected"
            : "Connecting..."}
        </span>

      </div>


      <div className="flex items-center -space-x-2">

        {users.length === 0 && (
          <span className="text-xs text-slate-400">
            Just you
          </span>
        )}


        {users.map((name, i) => (
          <span
            key={i}
            title={name}
            className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-medium text-white border-2 border-white dark:border-slate-900"
            style={{
              backgroundColor: colorFor(name),
            }}
          >
            {name
              .slice(0, 2)
              .toUpperCase()}
          </span>
        ))}

      </div>

    </div>
  );
}