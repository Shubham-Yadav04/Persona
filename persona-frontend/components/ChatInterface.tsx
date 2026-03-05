"use client";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, User, Bot } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import Error from "next/error";
import axios from "axios";

type Message = {
  id: string;
  role: "user" | "bot";
  content: string;
};
export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "bot",
      content: "Hi there, I am Shubham Yadav 's virtual Persona. How may I assist you today?",
    },
  ]);
  const [sessionId,setSessionId]= useState<string>(crypto.randomUUID());
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
const [response,setResponse]=  useState(false);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend =async () => {
    console.log(input);
    if (!input.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, newMessage]);
    setResponse(true);
    const userQuery=input;
setInput("")
    // Simulate bot response
    try{
        console.log('sending request to ' ,process.env.NEXT_PUBLIC_BACKEND_URI)
const res= await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URI}?q=${userQuery}`,{
  sessionId
});
console.log(res);
setResponse(false);
const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: res.data,
      };
      setMessages((prev) => [...prev, botResponse]);
    }
    catch(error:unknown){
      console.log(error);
      if(error instanceof Error )console.log(error)
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4 md:p-6 relative z-10">
      <div className=" relative flex-1 overflow-y-auto space-y-6  pb-20 scrollbar-none min-h[100vh]">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
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
                  message.role === "bot" ? "bg-black/50" : "bg-white/10"
                )}
              >
                {message.role === "bot" ? (
                  <Sparkles className="w-5 h-5 text-brown-800" />
                ) : (
                  <User className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div
                className={cn(
                  "relative max-w-[80%] md:max-w-[70%] p-4 rounded-2xl text-sm md:text-base leading-relaxed backdrop-blur-md border",
                  message.role === "bot"
                    ? "bg-white/5 border-white/10 rounded-tl-none text-gray-200"
                    : "bg-white/10 border-white/20 rounded-tr-none text-white shadow-[0_0_15px_rgba(255,255,255,0.1)]"
                )}
              >
                {message.content}
              
              </div>
            </motion.div>
          ))}
          {
              
                  response &&   <div
               
                className={cn(
                  "relative max-w-[80%] md:max-w-[70%] p-4 rounded-2xl text-sm md:text-base leading-relaxed backdrop-blur-md border",
                    "bg-white/5 border-white/10 rounded-tl-none text-gray-200 flex flex-row gap items-end gap-2"
                    
                )}
              >Searching <motion.h1
                  animate={{
    opacity: [0.2, 1, 0.2],
    scaleY: [0.2, 1, 0.2],
  }}
  transition={{
    duration: 1,
    ease: "easeInOut",
    repeat: Infinity,
    repeatType: "loop"
  }}
  className="w-fit text-md text-start text-neutral-400"
                >...</motion.h1>
              </div>
                
          }
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
            disabled={!input.trim()}
          >
            <Send className="w-4 h-4 ml-0.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
