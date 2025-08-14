'use client';

import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';

interface Document {
  id: string;
  title: string;
  source_type: string;
  status: string;
  storage_path?: string | null;
  url?: string | null;
  error?: string | null;
  created_at: string;
}

function formatDate(date: string): string {
  return new Date(date).toLocaleString();
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Document[]>([]);

  const fetchDocuments = useCallback(async () => {
    const token = localStorage.getItem('token');
    const res = await axios.get<Document[]>('http://localhost:8000/documents', {
      headers: { Authorization: token ? `Bearer ${token}` : '' },
    });
    setDocs(res.data);
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleDelete = async (id: string) => {
    const confirmed = window.confirm('Delete this document?');
    if (!confirmed) return;
    const token = localStorage.getItem('token');
    await axios.delete(`http://localhost:8000/documents/${id}`, {
      headers: { Authorization: token ? `Bearer ${token}` : '' },
    });
    fetchDocuments();
  };

  return (
    <div>
      <h1 className="text-2xl mb-4">Documents</h1>
      {docs.length === 0 ? (
        <p>No documents found.</p>
      ) : (
        <ul className="space-y-2">
          {docs.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between border p-2"
            >
              <div>
                <p>{doc.title}</p>
                <p className="text-sm text-gray-500">
                  {formatDate(doc.created_at)}
                </p>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="text-red-500"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

