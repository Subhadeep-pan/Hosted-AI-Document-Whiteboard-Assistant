import { useDropzone } from "react-dropzone";
import { FaFileAlt, FaTrash, FaCloudUploadAlt } from "react-icons/fa";

export default function DocumentPanel({ documents, uploadMessage, onUpload, onDelete, onSummarize, onReset }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    onDrop: onUpload,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`flex flex-col items-center gap-1 border-2 border-dashed rounded-xl p-4 text-center text-sm cursor-pointer transition-colors mb-3 ${
          isDragActive
            ? "border-accent-500 bg-accent-50 dark:bg-accent-700/10"
            : "border-slate-300 dark:border-slate-700 hover:border-accent-400 hover:bg-slate-50 dark:hover:bg-slate-800/40"
        }`}
      >
        <input {...getInputProps()} />
        <FaCloudUploadAlt className="text-xl text-slate-400" />
        <span>Drop files or click to upload</span>
        <span className="text-xs text-slate-400">PDF - DOCX - TXT</span>
      </div>

      {uploadMessage && <p className="text-xs text-slate-400 mb-2">{uploadMessage}</p>}

      <h2 className="text-xs font-medium uppercase tracking-wide text-slate-400 mb-1.5">Documents</h2>

      <div className="max-h-40 overflow-y-auto">
        {documents.length === 0 && <p className="text-sm text-slate-400">No documents uploaded yet.</p>}

        <ul className="space-y-0.5">
          {documents.map((doc, index) => (
            <li
              key={index}
              onClick={() => onSummarize(doc)}
              title={`Summarize ${doc}`}
              className="group flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm cursor-pointer truncate transition-colors hover:bg-slate-100 dark:hover:bg-slate-800/60"
            >
              <span className="flex items-center gap-2 truncate">
                <FaFileAlt className="text-accent-500 shrink-0" size={13} />
                <span className="truncate">{doc}</span>
              </span>

              <button
                onClick={(e) => onDelete(doc, e)}
                className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-opacity shrink-0"
                title="Delete this document"
              >
                <FaTrash size={11} />
              </button>
            </li>
          ))}
        </ul>
      </div>

      {documents.length > 0 && (
        <button
          onClick={onReset}
          className="mt-3 flex items-center gap-2 text-sm py-2 px-1 text-slate-400 hover:text-red-500 transition-colors"
        >
          <FaTrash size={11} /> Reset documents
        </button>
      )}
    </div>
  );
}
