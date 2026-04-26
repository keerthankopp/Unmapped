import React, { useMemo, useState } from "react";
import ErrorCard from "../shared/ErrorCard";

export default function ConversationalIntake({ hook }) {
  const { messages, sendMessage, isStreaming, isProfileReady, error } = hook;
  const [text, setText] = useState("");

  const canSend = useMemo(() => text.trim().length > 0 && !isStreaming, [text, isStreaming]);

  let errorDetail = null;
  if (error?.message) {
    errorDetail = error.message;
    try {
      const parsed = JSON.parse(error.message);
      if (parsed?.error) errorDetail = parsed.error;
    } catch {
      // keep raw string
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {error ? (
        <ErrorCard
          message={errorDetail ? `Intake failed: ${errorDetail}` : "Could not reach intake service"}
          endpoint="Claude / FastAPI"
          action="Check backend logs, API key, or try again"
        />
      ) : null}

      <div className="bg-white shadow-sm rounded-2xl p-3 flex flex-col gap-2">
        <div className="text-sm text-slate-500">Skills intake chat</div>
        <div className="flex flex-col gap-2 max-h-[55vh] overflow-auto pr-1">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={[
                "max-w-[92%] rounded-2xl px-3 py-2 text-sm leading-snug",
                m.role === "user" ? "self-end bg-teal-700 text-white" : "self-start bg-slate-100 text-slate-800"
              ].join(" ")}
            >
              {m.content}
            </div>
          ))}
        </div>
        {isProfileReady ? (
          <div className="text-xs text-slate-400 italic mt-1">Mapping complete.</div>
        ) : isStreaming ? (
          <div className="text-xs text-slate-400 italic mt-1">Mapping your skills…</div>
        ) : null}
      </div>

      <div className="bg-white shadow-sm rounded-2xl p-3 flex gap-2">
        <input
          className="flex-1 border border-slate-200 rounded-xl px-3 py-2 text-sm"
          placeholder="Type your answer…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && canSend) {
              sendMessage(text.trim());
              setText("");
            }
          }}
        />
        <button
          className={[
            "px-4 py-2 rounded-xl text-sm font-semibold",
            canSend ? "bg-teal-700 text-white" : "bg-slate-200 text-slate-500"
          ].join(" ")}
          disabled={!canSend}
          onClick={() => {
            sendMessage(text.trim());
            setText("");
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

