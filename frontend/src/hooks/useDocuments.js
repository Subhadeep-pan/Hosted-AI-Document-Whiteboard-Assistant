import { useState, useEffect } from "react";
import { getDocuments, deleteDocument } from "../api/docsApi";
import { uploadFile } from "../api/uploadApi";
import { resetProject } from "../api/resetApi";

export default function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [uploadMessage, setUploadMessage] = useState("");

  useEffect(() => {
    getDocuments().then(setDocuments).catch(() => {});
  }, []);

  const upload = async (files) => {
    if (!files || files.length === 0) return;

    try {
      const result = await uploadFile(files);
      setUploadMessage(result.message);
      setDocuments(await getDocuments());
    } catch {
      setUploadMessage("Upload failed.");
    }
  };

  const remove = async (docId) => {
    await deleteDocument(docId);
    setDocuments((prev) => prev.filter((doc) => doc !== docId));
  };

  const resetAll = async () => {
    try {
      const result = await resetProject();
      setDocuments([]);
      setUploadMessage(result.message);
    } catch {
      setUploadMessage("Reset failed.");
    }
  };

  return { documents, uploadMessage, upload, remove, resetAll };
}
