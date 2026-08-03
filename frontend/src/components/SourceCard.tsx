import { cn } from "../lib/utils";
import { FileText, ExternalLink } from "lucide-react";

interface SourceCardProps {
  title: string;
  excerpt: string;
  relevanceScore?: number;
  className?: string;
}

export function SourceCard({ title, excerpt, relevanceScore, className }: SourceCardProps) {
  return (
    <div className={cn("p-4 rounded-xl bg-card border border-border shadow-lg shadow-black/20 group hover:border-primary/50 transition-colors", className)}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2 text-sm font-medium text-primary">
          <FileText className="w-4 h-4" />
          <span>{title}</span>
        </div>
        {relevanceScore !== undefined && (
          <span className="text-xs px-2 py-1 bg-white/5 rounded-full border border-white/10 text-zinc-300">
            {Math.round(relevanceScore * 100)}% Match
          </span>
        )}
      </div>
      <p className="text-sm text-zinc-400 line-clamp-3 leading-relaxed">
        {excerpt}
      </p>
      <button className="mt-3 text-xs flex items-center gap-1 text-zinc-500 hover:text-zinc-300 transition-colors opacity-0 group-hover:opacity-100">
        View source <ExternalLink className="w-3 h-3" />
      </button>
    </div>
  );
}
