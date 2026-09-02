import { useState } from "react";
import { FaChalkboard } from "react-icons/fa";

function randomRoomId() {
  return Math.random().toString(36).slice(2, 8);
}

// Professional collaborative apps (Google Docs, Figma, etc) never make
// you type a name before you can join - they generate a friendly guest
// name up front and let you change it if you want. Matches that.
const GUEST_ADJECTIVES = ["Swift", "Clever", "Bright", "Bold", "Calm", "Quick", "Sharp", "Sunny"];
const GUEST_ANIMALS = ["Falcon", "Otter", "Fox", "Panda", "Wolf", "Hawk", "Tiger", "Lynx"];

function randomGuestName() {
  const adjective = GUEST_ADJECTIVES[Math.floor(Math.random() * GUEST_ADJECTIVES.length)];
  const animal = GUEST_ANIMALS[Math.floor(Math.random() * GUEST_ANIMALS.length)];
  const number = Math.floor(Math.random() * 90) + 10;
  return `${adjective}${animal}${number}`;
}

export default function RoomJoin({ onJoin }) {
  const [roomId, setRoomId] = useState(randomRoomId());
  const [name, setName] = useState(localStorage.getItem("whiteboard_name") || randomGuestName());

  const handleJoin = () => {
    if (!name.trim()) return;
    localStorage.setItem("whiteboard_name", name.trim());
    onJoin(roomId.trim(), name.trim());
  };

  return (
    <div className="flex h-screen items-center justify-center bg-slate-50 dark:bg-slate-950">
      <div className="w-full max-w-sm rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6">
        <div className="flex items-center gap-2 mb-5">
          <span className="w-9 h-9 rounded-xl bg-accent-100 dark:bg-accent-700/30 text-accent-600 dark:text-accent-200 flex items-center justify-center">
            <FaChalkboard size={15} />
          </span>
          <h2 className="text-lg font-semibold">Collaborative whiteboard</h2>
        </div>

        <label className="text-xs font-medium uppercase tracking-wide text-slate-400">Your name</label>
        <input
          autoFocus
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleJoin()}
          placeholder="e.g. Priya"
          className="w-full rounded-lg px-3 py-2 mt-1 mb-4 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 outline-none focus:ring-2 focus:ring-accent-500"
        />

        <label className="text-xs font-medium uppercase tracking-wide text-slate-400">Room code</label>
        <input
          value={roomId}
          onChange={(e) => setRoomId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleJoin()}
          className="w-full rounded-lg px-3 py-2 mt-1 mb-1 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 outline-none focus:ring-2 focus:ring-accent-500 font-mono"
        />
        <p className="text-xs text-slate-400 mb-5">Share this code with others so they join the same board.</p>

        <button
          onClick={handleJoin}
          disabled={!name.trim()}
          className="w-full py-2.5 rounded-xl bg-accent-600 hover:bg-accent-700 disabled:opacity-50 text-white font-medium transition-colors"
        >
          Join whiteboard
        </button>
      </div>
    </div>
  );
}
