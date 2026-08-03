import { cn } from "../lib/utils";

interface CitationChipProps {
  number: number;
  onClick?: () => void;
  className?: string;
}

export function CitationChip({ number, onClick, className }: CitationChipProps) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "inline-flex items-center justify-center w-5 h-5 ml-1 text-[10px] font-bold",
        "bg-primary/20 text-primary border border-primary/30 rounded-full",
        "hover:bg-primary hover:text-primary-foreground transition-all duration-200 transform hover:scale-110",
        "align-super cursor-pointer",
        className
      )}
    >
      {number}
    </button>
  );
}
