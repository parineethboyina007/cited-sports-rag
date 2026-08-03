import { DatasetBrowser } from "./components/DatasetBrowser";
import { ChatWindow } from "./components/ChatWindow";

function App() {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30">
      {/* Sidebar - Dataset Browser */}
      <div className="w-72 shrink-0 hidden md:block">
        <DatasetBrowser />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <ChatWindow />
      </div>
    </div>
  );
}

export default App;
