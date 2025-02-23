import {useState} from "react";
import axios from "axios";

const ChatBox = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    
    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        try {
            const response = await axios.post("http://localhost:5000/chat", {
                messages: input,
            });

            const botMessage = { role: "assistant", content: response.data.reply };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error("Error sending message:", error);
        }

        setInput("");
    };

    return (
        <div className="p-4 bg-gray-100 h-full flex flex-col">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`p-2 my-1 rounded-lg ${
                        msg.role === "user" ? "bg-blue-500 text-white self-end" : "bg-gray-300 text-black self-start"
                        }`}
                     >
                        {msg.content}
                    </div>
                ))}
            </div>

            {/* Chat Input */}
            <div className="mt-auto">
                <input
                    type="text"
                    className="w-full p-2 rounded-lg border-2 border-gray-300"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your response..."
                />
                <button
                    onClick={sendMessage}
                    className="ml-2 px-4 py-2 bg-blue-500 text-white rounded-lg"
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatBox;