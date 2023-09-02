// Based on https://medium.com/@yuhaocooper/how-to-deploy-react-app-on-aws-lightsail-and-build-your-own-website-d4937c5c8792

// Development (Laptop)
// cd /Users/smccann/Desktop/CypressLabs/jarvis
// Make edits
// npm start
// When ready to deploy
// git status 
// git commit -m "Add Jarvis version"
// git push origin main  

// Server
// cd /opt/jarvis
// sudo git pull origin main
// sudo npm install
// sudo npm run build
// sudo systemctl restart nginx

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

const JarvisClient = () => {
  const [userMessage, setUserMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatLog]);

  const sendMessage = async () => {
    if (userMessage.trim() === "") return;
    setChatLog([...chatLog, { type: "user", text: userMessage }]);
    setUserMessage("");

    try {
      console.log("Sending message to server:", userMessage)
      const response = await axios.post("http://127.0.0.1:5000/api/chat", {
        message: userMessage,
      });
      console.log("Received response from server:", response)
      setChatLog([...chatLog, { type: "user", text: userMessage }, { type: "gpt", text: response.data.response }]);
    } 
    catch (error) {
      console.log("Error while sending message:", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Jarvis</h1>
      </header>
      <main>
        <div className="chat-log">
          {chatLog.map((message, index) => (
            <div key={index} className={`chat-message ${message.type}`}>
              {message.text}
            </div>
          ))}
          <div ref={messagesEndRef}></div>
        </div>
        <div className="input-form">
          <input
            type="text"
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </main>
    </div>
  );
};

export default JarvisClient;
