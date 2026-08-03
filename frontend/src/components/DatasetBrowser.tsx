import { useEffect, useState } from "react";
import { cn } from "../lib/utils";

interface DatasetBrowserProps {
  className?: string;
}

interface PlayerSummary {
  id: string;
  name: string;
  category: string;
  dataset: string;
}

export function DatasetBrowser({ className }: DatasetBrowserProps) {
  const [players, setPlayers] = useState<PlayerSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/players")
      .then(res => res.json())
      .then(data => {
        setPlayers(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className={cn("flex flex-col h-full bg-card/50 backdrop-blur-md border-r border-border p-4", className)}>
      <h2 className="text-lg font-semibold mb-4 tracking-tight">Database Entities</h2>
      <div className="flex-1 overflow-y-auto space-y-2 pr-2">
        {loading ? (
          <p className="text-sm text-zinc-400">Loading players...</p>
        ) : (
          players.map(p => (
            <div key={p.id} className="p-3 rounded-md bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-pointer group">
              <p className="text-sm font-medium text-zinc-200 group-hover:text-primary transition-colors">{p.name}</p>
              <div className="flex items-center justify-between mt-1">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500">{p.category}</span>
                <span className="text-[10px] font-mono text-zinc-500">{p.id}</span>
              </div>
            </div>
          ))
        )}
      </div>
      <div className="mt-4 w-full py-3 px-4 bg-primary/5 rounded-md text-xs text-center text-zinc-400 border border-primary/10">
        Loaded {players.length} entities
      </div>
    </div>
  );
}
