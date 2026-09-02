import { FaRobot } from "react-icons/fa";

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center text-center mt-24">
      <span className="w-14 h-14 rounded-2xl bg-accent-100 dark:bg-accent-700/30 text-accent-600 dark:text-accent-200 flex items-center justify-center mb-4">
      </span>
      <h2 className="text-xl font-semibold mb-1.5">Welcome to AI resume assistant</h2>
      <p className="text-slate-400 text-sm">Upload documents and ask questions to get started.</p>
    </div>
  );
}
