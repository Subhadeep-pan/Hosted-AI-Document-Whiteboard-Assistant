import { useState } from "react";
import { FaThumbsUp, FaThumbsDown, FaFileAlt, FaTools } from "react-icons/fa";

import { sendFeedback } from "../../api/feedbackApi";

export default function MessageMeta({ question, answer, meta }) {
  const [feedbackGiven, setFeedbackGiven] = useState(null);

  if (!meta) return null;

  const { tools_used: toolsUsed, sources, confidence } = meta;

  const handleFeedback = async (helpful) => {
    setFeedbackGiven(helpful);
    try {
      await sendFeedback(question, answer, helpful);
    } catch {
      // Best-effort - don't interrupt the chat if it fails.
    }
  };

  return (
    <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-400">
      {toolsUsed?.length > 0 && (
        <span className="flex items-center gap-1">
          <FaTools size={10} /> {toolsUsed.join(", ")}
        </span>
      )}

      {sources?.length > 0 && (
        <span className="flex items-center gap-1">
          <FaFileAlt size={10} /> {sources.join(", ")}
        </span>
      )}

      {confidence && <span>confidence: {confidence}</span>}

      <span className="flex items-center gap-2 ml-auto">
        <button
          onClick={() => handleFeedback(true)}
          className={`hover:text-green-500 transition-colors ${feedbackGiven === true ? "text-green-500" : ""}`}
          title="Helpful"
        >
          <FaThumbsUp size={12} />
        </button>
        <button
          onClick={() => handleFeedback(false)}
          className={`hover:text-red-500 transition-colors ${feedbackGiven === false ? "text-red-500" : ""}`}
          title="Not helpful"
        >
          <FaThumbsDown size={12} />
        </button>
      </span>
    </div>
  );
}
