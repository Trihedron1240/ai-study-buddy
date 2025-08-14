'use client';

import { useState } from 'react';
import axios, { AxiosError } from 'axios';

interface SearchResult {
  document_id: string;
  document_title: string;
  content: string;
  score: number;
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setError(null);
    setResults([]);
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post<SearchResult[] | { results: SearchResult[] }>(
        'http://localhost:8000/search',
        { query, top_k: 10 },
        { headers: { Authorization: token ? `Bearer ${token}` : '' } }
      );
      const data = Array.isArray(res.data) ? res.data : res.data.results;
      setResults(data);
    } catch (err: unknown) {
      const detail =
        (err as AxiosError<{ detail?: string }>).response?.data?.detail;
      setError(detail ?? 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl mb-4">Search</h1>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-grow border p-2"
          placeholder="Enter query"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      {error && <p className="text-red-500">{error}</p>}
      <ul className="space-y-4">
        {results.map((hit) => (
          <li key={hit.document_id} className="border p-2">
            <p className="font-semibold">
              {hit.document_title || hit.document_id}
            </p>
            <p className="text-sm text-gray-500">
              Score: {hit.score.toFixed(3)}
            </p>
            <p className="whitespace-pre-wrap">{hit.content}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

