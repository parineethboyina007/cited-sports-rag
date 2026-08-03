import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { cn } from "../lib/utils";
import { CitationChip } from "./CitationChip";

interface ChatWindowProps {
  className?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: string[];
}

export function ChatWindow({ className }: ChatWindowProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: data.answer, 
        citations: data.citations 
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: "assistant", content: "Error connecting to the API." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col h-full bg-background relative", className)}>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[80%] h-[200px] bg-primary/10 blur-[100px] pointer-events-none rounded-full" />
      
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 z-10">
        {messages.length === 0 && (
          <div className="text-center text-zinc-500 mt-20">
            Ask me anything about cricketers or Olympic athletes!
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className="flex gap-4 max-w-3xl mx-auto">
            <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0", 
              msg.role === "user" ? "bg-zinc-800" : "bg-primary/20 border border-primary/30"
            )}>
              {msg.role === "user" ? <User className="w-4 h-4 text-zinc-400" /> : <Bot className="w-4 h-4 text-primary" />}
            </div>
            <div className="pt-1 text-zinc-200 leading-relaxed whitespace-pre-wrap">
              {msg.content}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {msg.citations.map((c, idx) => (
                    <span key={idx} className="px-2 py-1 bg-zinc-800 rounded-md text-xs font-mono text-zinc-400 border border-zinc-700">
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-4 max-w-3xl mx-auto">
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="pt-1">
              <Loader2 className="w-5 h-5 text-primary animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-background/80 backdrop-blur-xl border-t border-border z-10">
        <div className="max-w-3xl mx-auto relative group flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask a question about the encyclopedia..."
            className="w-full bg-card border border-border rounded-full py-4 pl-6 pr-14 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all shadow-lg"
          />
          <button 
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 transition-colors shadow-md group-focus-within:scale-105 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
