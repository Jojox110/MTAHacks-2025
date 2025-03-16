import { ChatInput } from "@/components/custom/chatinput";
import { PreviewMessage, ThinkingMessage } from "../../components/custom/message";
import { useScrollToBottom } from '@/components/custom/use-scroll-to-bottom';
import { useState, useRef } from "react";
import { message } from "../../interfaces/interfaces";
import { Overview } from "@/components/custom/overview";
import { Header } from "@/components/custom/header";
import { v4 as uuidv4 } from 'uuid';

export function Chat() {
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();
  const [messages, setMessages] = useState<message[]>([]);
  const [question, setQuestion] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  async function handleSubmit(text?: string) {
    const messageText = text || question;
    if (!messageText.trim() || isLoading) return;
    setIsLoading(true);
    
    // Generate a unique ID for the user message.
    const userId = uuidv4();
    // Add the user message to the chat
    setMessages(prev => [
      ...prev, 
      { content: messageText, role: "user", id: userId }
    ]);
    setQuestion("");

    try {
      const response = await queryOllama(messageText);
      // Extract the reply from the response.
      const reply = response.answer || response.message || response;
      
      // Generate a separate ID for the assistant's reply.
      const assistantId = uuidv4();
      // Append the assistant's reply as a separate chat bubble.
      setMessages(prev => [
        ...prev, 
        { content: reply, role: "assistant", id: assistantId }
      ]);
      setIsLoading(false);
    } catch (error) {
      console.error("Error querying Ollama:", error);
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-[url('src/assets/imgs/background_dimmed_dimmed.jpg')]">
      {/* <Header /> */}
      <div className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4" ref={messagesContainerRef}>
        {messages.length === 0 && <Overview />}
        {messages.map((msg) => (
          <PreviewMessage key={msg.id} message={msg} />
        ))}
        {isLoading && <ThinkingMessage />}
        <div ref={messagesEndRef} className="shrink-0 min-w-[24px] min-h-[24px]" />
      </div>
      <div className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <ChatInput  
          question={question}
          setQuestion={setQuestion}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

async function queryOllama(message: string) {
  let answer;
  console.log("Querying Ollama with:", message);

  await fetch("http://localhost:5000/ollama", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  })
    .then((res) => res.json())
    .then((res) => {
      answer = res;
    })
    .catch((err) => {
      console.error("Fetch error:", err);
    });
  return answer;
}
