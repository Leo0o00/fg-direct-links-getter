"use client";
import { useState } from "react";
// TODO: Personalizar un poco la pagina
// TODO: Implemetar la cache
export default function Home() {
  const [url, setUrl] = useState("");
  const [links, setLinks] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true); setError(""); setLinks([]);
    // console.log("inputUrls: ", url);
    // console.log("inputUrlsType: ", typeof url);
    const splitedUrls: string[] = url.split("\n");
    console.log("splitedUrls: ", splitedUrls);

    const res = await fetch("http://localhost:8000/api/direct-links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: splitedUrls })
    });
    if (!res.ok) {
      setError("Invalid FitGirl URL or server error");
    } else {
      const data = await res.json();
      setLinks(data.links);
    }
    setLoading(false);
  }

  return (
    <main className="min-h-screen flex flex-col items-center gap-10 p-6">
      <h1 className="text-3xl font-bold">FuckingFast Direct Links Finder</h1>

      {/* form */}
      <form onSubmit={handleSubmit} className="flex gap-4 w-full max-w-xl">
        <textarea
          
          aria-multiline
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://fuckingfast.co/..."
          className="flex-grow border rounded px-3 py-2"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white rounded px-4"
        >
          {loading ? "Fetching…" : "Go"}
        </button>
      </form>

      {/* results */}
      {error && <p className="text-red-600">{error}</p>}
      {links.length > 0 && (
        <ul className="space-y-2 w-full max-w-xl">
          {links.map((l) => (
            <li key={l} className="break-all border p-2 rounded">
              <a href={l} className="text-blue-700 underline" target="_blank" rel="noreferrer">
                {l}
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}