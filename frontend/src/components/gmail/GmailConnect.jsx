import { useState, useEffect } from "react";
import { FaEnvelope } from "react-icons/fa";

import { getGmailStatus, getGmailConnectUrl, disconnectGmail } from "../../api/gmailApi";

export default function GmailConnect() {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGmailStatus()
      .then(setConnected)
      .catch(() => setConnected(false))
      .finally(() => setLoading(false));
  }, []);

  const handleConnect = async () => {
    const url = await getGmailConnectUrl();
    window.location.href = url;
  };

  const handleDisconnect = async () => {
    await disconnectGmail();
    setConnected(false);
  };

  if (loading) return null;

  return (
    <div className="flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm mb-3 bg-slate-100 dark:bg-slate-800/60">
      <span className="flex items-center gap-2 truncate">
        <FaEnvelope size={12} className={connected ? "text-green-500" : "text-slate-400"} />
        Gmail {connected ? "connected" : "not connected"}
      </span>

      {connected ? (
        <button onClick={handleDisconnect} className="text-xs text-red-500 hover:underline shrink-0">
          Disconnect
        </button>
      ) : (
        <button onClick={handleConnect} className="text-xs text-accent-600 hover:underline shrink-0">
          Connect
        </button>
      )}
    </div>
  );
}
