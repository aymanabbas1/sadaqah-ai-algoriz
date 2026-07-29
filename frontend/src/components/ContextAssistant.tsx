import { FormEvent, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { api } from "../lib/api";
import type { SourceRecord } from "../lib/types";

type Message = {
  id: number;
  role: "user" | "assistant";
  text: string;
  sources?: SourceRecord[];
};

type Props = {
  title: string;
  subtitle: string;
  contextType: "crisis" | "ngo_comparison";
  crisisId?: string;
  ngoIds?: string[];
  prompts: string[];
};

const isReadableSource = (url: string) => !url.includes("api.hpc.tools") && !url.includes("api.unhcr.org");

export default function ContextAssistant({ title, subtitle, contextType, crisisId, ngoIds = [], prompts }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState(false);
  const contextKey = `${contextType}:${crisisId ?? "none"}:${ngoIds.join(",")}`;

  useEffect(() => {
    setMessages([]);
    setError(false);
  }, [contextKey]);

  const ask = async (question: string) => {
    const clean = question.trim();
    if (!clean || isThinking) return;
    const history = messages.map((message) => ({ role: message.role, content: message.text }));
    setMessages((current) => [...current, { id: Date.now(), role: "user", text: clean }]);
    setInput("");
    setError(false);
    setIsThinking(true);
    try {
      const response = await api.chat({ message: clean, contextType, crisisId, ngoIds, conversation: history });
      setMessages((current) => [...current, {
        id: Date.now() + 1,
        role: "assistant",
        text: response.message,
        sources: response.sources,
      }]);
    } catch {
      setError(true);
    } finally {
      setIsThinking(false);
    }
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void ask(input);
  };

  return (
    <section className="context-assistant">
      <header>
        <span className="mansa-avatar"><b>MM</b><i /></span>
        <div><p>Mansa Musa</p><h2>{title}</h2><small>{subtitle}</small></div>
        <em>Research assistant</em>
      </header>
      <div className="context-chat" aria-live="polite">
        {messages.length === 0 && !isThinking && <p className="context-empty">{contextType === "crisis" ? "Ask about this crisis, responding organizations, or official sources." : "Ask about the selected NGOs, their published figures, or official reports."}</p>}
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div className={`context-message ${message.role}`} key={message.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <p>{message.text}</p>
              {message.sources && message.sources.length > 0 && (
                <div className="context-sources">
                  {message.sources.filter((source) => isReadableSource(source.url)).slice(0, 4).map((source) => <a href={source.url} target="_blank" rel="noreferrer" key={source.url}>{source.organization}<span>{source.title}</span></a>)}
                </div>
              )}
            </motion.div>
          ))}
          {isThinking && <motion.div className="context-thinking" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><i /><i /><i /><span>Retrieving sourced information</span></motion.div>}
        </AnimatePresence>
        {error && <div className="api-error"><strong>Assistant unavailable</strong><span>The profiles and source links remain available above.</span></div>}
      </div>
      <div className="context-prompts">{prompts.map((prompt) => <button onClick={() => void ask(prompt)} type="button" key={prompt}>{prompt}</button>)}</div>
      <form onSubmit={submit}><input aria-label="Ask Mansa Musa" placeholder="Ask about the selected information..." value={input} onChange={(event) => setInput(event.target.value)} /><button disabled={!input.trim() || isThinking} type="submit">Ask <span aria-hidden="true">{"->"}</span></button></form>
    </section>
  );
}
