import React from "react";

export default function ConfirmModal({ message, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-xl p-6 w-[90%] max-w-sm border border-slate-200">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          {message}
        </h3>
        <div className="flex justify-center gap-3">
          <button
            onClick={onCancel}
            className="px-6 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-900 font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 rounded-full bg-slate-900 hover:bg-slate-800 text-white font-medium transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}