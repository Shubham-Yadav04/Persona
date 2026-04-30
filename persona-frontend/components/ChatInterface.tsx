"use client";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, User, Bot } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import Error from "next/error";


type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  loading?: boolean;
};
export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId,setSessionId]= useState<string>(crypto.randomUUID());
  const [input, setInput] = useState("");
  const controllerRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
const [response,setResponse]=  useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend =async () => {
    controllerRef.current?.abort(); // cancel previous
controllerRef.current = new AbortController();
    if (response) return;
    if (!input.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };
    setMessages((prev: Message[]) => [...prev || [], newMessage]);
    setResponse(true);
    const userQuery=input;
setInput("")
    // Simulate bot response
    let botMessageId: string | null;
try {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URI}`, {
    method: "POST",
    body: JSON.stringify({ sessionId, query: userQuery }),
    headers: {
      "Content-Type": "application/json",
    },
   signal: controllerRef.current.signal,
    cache:"no-cache"
  });

  if (!res.ok) throw new Error("Request failed");

  if (!res.body) throw new Error("No response body"); 
  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let fullResponse = "";
  let buffer="";
  // Add empty bot message first
   botMessageId = Date.now().toString();
  setMessages(prev => [
  ...(prev || []),
  {
    id: botMessageId,
    role: "assistant",
    content: "",
    loading: true
  }
]);

  while (true) {
  const { value, done } = await reader.read();
  if (done){
    break;
  } 

  buffer += decoder.decode(value, { stream: true });

  // Split complete SSE messages
  const parts = buffer.split("\n");
  buffer = parts.pop();

  for (const part of parts) {
    if (part.startsWith("data:")) {
  const data = part.replace("data:", "").trim();

  fullResponse += data;

  setMessages((prev: Message[]) =>
    prev?.map(msg =>
      msg.id === botMessageId
        ? {
            ...msg,
            content: fullResponse,
            loading: false, // remove searching
          }
        : msg
    )
  );
}
  }
}

  setResponse(false);

}
 catch (error) {
  console.log(error);
  setResponse(false);
 
  setMessages((prev: Message[]) =>
    prev?.map(msg=> msg.id===botMessageId!?
      {...msg, content:"Sorry, something went wrong. Please try again."}
      :msg
    ) 
  )
  };
}
return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4 md:p-6 relative z-10">
      <div className=" relative flex-1 overflow-y-auto space-y-6  pb-20 scrollbar-none min-h[100vh]">
        <AnimatePresence initial={false}>
        {
          messages.length===0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}    
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="flex flex-col items-center gap-4 mt-20 text-gray-500"
            > 
              <Bot className="w-10 h-10 text-gray-400" />
              <p className="text-lg">How can i Help You </p>
            </motion.div>
          )
        }
          {messages?.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className={cn(
                "flex items-start gap-4",
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              )}
            >
              <div
                className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center shrink-0 border border-white/10",
                  message.role === "assistant" ? "bg-black/50" : "bg-white/10"
                )}
              >
                {message.role === "assistant" ? (
                  <Sparkles className="w-5 h-5 text-brown-800" />
                ) : (
                  <User className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div
                className={cn(
                  "relative max-w-[80%] md:max-w-[70%] p-4 rounded-2xl text-sm md:text-base leading-relaxed backdrop-blur-md ",
                  message.role === "assistant"
                    ? "text-gray-200"
                    : "bg-white/10 border border-white/20 rounded-tr-none text-white shadow-[0_0_15px_rgba(255,255,255,0.1)]"
                )}
              >
                {message.loading ? (
  <span className="animate-pulse text-gray-400">
    Searching<span className="animate-bounce">...</span>
  </span>
) : (
  message.content
)}
              
              </div>
            </motion.div>
          ))}
         
        </AnimatePresence>
        <div ref={messagesEndRef}  className="absolute bottom-5 left-0 pb-10 "/>
      </div>

      <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black via-black/80 to-transparent pt-20">
        <div className="max-w-3xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Initialize interaction..."
            className="w-full bg-white/5 border border-white/10 rounded-full px-6 py-4 pr-16 text-white placeholder:text-gray-500 focus:outline-none focus:border-white/20 focus:bg-white/10 focus:ring-1 focus:ring-white/20 transition-all backdrop-blur-xl shadow-2xl"
          />
          <button
            onClick={handleSend}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-white text-black rounded-full flex items-center justify-center hover:scale-105 hover:bg-gray-200 transition-all disabled:opacity-50 disabled:hover:scale-100"
            disabled={!input.trim()  || response}
          >
            <Send className="w-4 h-4 ml-0.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

