import { useState } from "react";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm Fonada AI Support. How can I help you today?"
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
  const message = input.trim();

  if (!message || loading) {
    return;
  }

  // Add user message
  setMessages((previous) => [
    ...previous,
    {
      role: "user",
      content: message
    }
  ]);

  setInput("");
  setLoading(true);

  try {
    const response = await fetch("/chat", {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        message: message
      })
    });

    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error("INVALID_SERVER_RESPONSE");
    }

    console.log("Backend response:", data);

      
    // HTTP ERROR
      

    if (!response.ok) {
      console.error("HTTP error:", data);

      throw new Error("SERVER_ERROR");
    }

      
    // GET RESPONSE
      

    const assistantResponse =
      typeof data.response === "string"
        ? data.response.trim()
        : "";

      
    // DETECT BACKEND/LLM ERROR INSIDE RESPONSE
      

    const isBackendError =
      assistantResponse.startsWith("Agent error:") ||
      assistantResponse.includes("RateLimitError") ||
      assistantResponse.includes("credit_balance_exhausted") ||
      assistantResponse.includes("insufficient_quota") ||
      assistantResponse.includes("BadRequestError") ||
      assistantResponse.includes("Internal Server Error") ||
      assistantResponse.includes("ExceptionGroup") ||
      assistantResponse.includes("Traceback") ||
      assistantResponse.includes("TaskGroup");

    if (isBackendError) {

      // Keep technical error in browser console
      console.error(
        "Backend/Agent error:",
        assistantResponse
      );

      // Show clean message to user
      throw new Error("AGENT_ERROR");
    }

      
    // OTHER BACKEND ERROR FORMAT
      

    if (data.error || data.detail) {

      console.error(
        "Backend error:",
        data.error || data.detail
      );

      throw new Error("AGENT_ERROR");
    }

      
    // EMPTY RESPONSE
      

    if (!assistantResponse) {
      throw new Error("EMPTY_RESPONSE");
    }

      
    // SUCCESS
      

    setMessages((previous) => [
      ...previous,
      {
        role: "assistant",
        content: assistantResponse
      }
    ]);

  } catch (error) {

      
    // NEVER SHOW RAW ERROR
      

    console.error(
      "Chat request failed:",
      error
    );

    let friendlyMessage =
      "Sorry, something went wrong. Please try again.";

    if (error.message === "Failed to fetch") {

      friendlyMessage =
        "I'm unable to connect to the support service right now. Please try again in a moment.";

    } else if (
      error.message === "SERVER_ERROR"
    ) {

      friendlyMessage =
        "The support service is temporarily unavailable. Please try again shortly.";

    } else if (
      error.message === "AGENT_ERROR"
    ) {

      friendlyMessage =
        "I'm unable to process your request right now. Please try again in a moment.";

    } else if (
      error.message === "INVALID_SERVER_RESPONSE"
    ) {

      friendlyMessage =
        "The support service returned an unexpected response. Please try again.";

    } else if (
      error.message === "EMPTY_RESPONSE"
    ) {

      friendlyMessage =
        "I couldn't generate a response for that request. Please try again.";
    }

      
    // SHOW FRIENDLY MESSAGE
      

    setMessages((previous) => [
      ...previous,
      {
        role: "assistant",
        content: friendlyMessage,
        isError: true
      }
    ]);

  } finally {
    setLoading(false);
  }
};


    
  // ENTER KEY
    

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  };


    
  // CLEAR CHAT
    

  const clearChat = () => {
    setMessages([
      {
        role: "assistant",
        content:
          "Hi! I'm Fonada AI Support. How can I help you today?"
      }
    ]);
  };


  return (
    <div className="app">


      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            F
          </div>

          <div>

            <h1>
              Fonada AI Support
            </h1>

            <div className="status">

              <span className="status-dot"></span>

              AI Agent Online

            </div>

          </div>

        </div>


        <button
          className="clear-button"
          onClick={clearChat}
        >
          Clear
        </button>

      </header>


      <main className="chat-container">


        {/* INTRO */}

        <section className="intro">

          <div className="intro-badge">
            AI SUPPORT AGENT
          </div>

          <h2>
            How can we help?
          </h2>

          <p>
            Ask about your support request or
            create a callback in seconds.
          </p>

        </section>


     

        <section className="messages">

          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={`message-row ${message.role}`}
              >

                {message.role ===
                  "assistant" && (

                  <div className="avatar">
                    F
                  </div>

                )}


                <div
                  className={`message ${message.role} ${
                    message.isError
                      ? "error-message"
                      : ""
                  }`}
                >
                  {message.content}
                </div>

              </div>

            )
          )}


          {/* LOADING */}

          {loading && (

            <div className="message-row assistant">

              <div className="avatar">
                F
              </div>

              <div className="message assistant typing">

                <span></span>
                <span></span>
                <span></span>

              </div>

            </div>

          )}

        </section>




        <div className="quick-actions">

          <button
            onClick={() =>
              setInput(
                "I need a callback for a support issue."
              )
            }
          >
            Request a callback
          </button>


          <button
            onClick={() =>
              setInput(
                "Can you check my previous callback request?"
              )
            }
          >
            Check my callback
          </button>


          <button
            onClick={() =>
              setInput(
                "Show me the available support options."
              )
            }
          >
            Support options
          </button>

        </div>


        <div className="input-wrapper">

          <textarea
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            rows="1"
            disabled={loading}
          />


          <button
            className="send-button"
            onClick={sendMessage}
            disabled={
              loading ||
              !input.trim()
            }
          >
            {loading
              ? "..."
              : "Send"}
          </button>

        </div>


        <p className="input-hint">
          Press Enter to send · Shift + Enter
          for a new line
        </p>

      </main>

      <footer>
        Fonada AI Agent · Powered by
        FastAPI + LLM + MCP
      </footer>

    </div>
  );
}

export default App;