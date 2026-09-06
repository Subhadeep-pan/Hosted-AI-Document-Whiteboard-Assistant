import api from "./api";

const META_DELIMITER = "\n<<<META>>>";

export const askQuestion = async (question, chatId) => {
  const response = await api.get("/ask", {
    params: { question, chat_id: chatId },
  });

  return response.data;
};

// Streams the answer back word-by-word, like ChatGPT "typing".
// onChunk is called with each new piece of visible text.
// onMeta (optional) is called once at the end with {tools_used, sources, confidence}.
export const askQuestionStream = async (question, chatId, onChunk, onMeta) => {
  const baseURL = api.defaults.baseURL;
  const sessionId = localStorage.getItem("session_id");

  const url = `${baseURL}/ask/stream?question=${encodeURIComponent(question)}&chat_id=${chatId}`;

  const response = await fetch(url, {
    headers: { "X-Session-Id": sessionId },
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Only flush text up to the delimiter (if it's arrived) - metadata
    // never gets shown as chat text, even if it arrives mid-chunk.
    const delimiterIndex = buffer.indexOf(META_DELIMITER);

    if (delimiterIndex === -1) {
      onChunk(buffer);
      buffer = "";
    } else {
      onChunk(buffer.slice(0, delimiterIndex));
      buffer = buffer.slice(delimiterIndex);
    }
  }

  const delimiterIndex = buffer.indexOf(META_DELIMITER);
  if (delimiterIndex !== -1 && onMeta) {
    try {
      const metaJson = buffer.slice(delimiterIndex + META_DELIMITER.length);
      onMeta(JSON.parse(metaJson));
    } catch {
      // If parsing fails, just skip the metadata - the chat text itself
      // already streamed fine above.
    }
  } else if (buffer && !delimiterIndex) {
    onChunk(buffer);
  }
};
