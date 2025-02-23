import { useState } from "react";
import axios from "axios";
import "./MessageBox.css";

const MessageBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const welcomeMessage = {
    text: "Hello! Welcome to EcoSim. I'm your virtual assistant. Feel free to ask questions about the simulation!",
    isSystem: true
  };

  const handleSend = async () => {
    if (input.trim() !== "") {
      setMessages([...messages, { text: input, isSystem: false }]);
      
      try {
        const response = await axios.post("http://localhost:5000/api/messages", {
          message: input
        });
        
        if (response.data.aiResponse) {
          setMessages(prev => [...prev, response.data.aiResponse]);
          console.log("AI Response:", response.data.aiResponse);
        }
      } catch (error) {
        console.error("Error sending message:", error);
      }
      
      setInput("");
    }
  };

  return (
    <div className="message-box-container">
      <div className="messages-container">
        <div className="message system-message">
          {welcomeMessage.text}
        </div>
        
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`message ${msg.isSystem ? 'system-message' : 'user-message'}`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          className="message-input"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend} className="send-button">
          Send
        </button>
      </div>
    </div>
  );
}

export default MessageBox;