import { useState, useMemo, useEffect } from "react";
import { CandyButton, CandyCard, CandySpotlightOverlay, AuroraRing } from "./components/candy/Candy";
import "./aura.css"; // Assuming base styles are in here

const App = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [currentActionIndex, setCurrentActionIndex] = useState(0);

  const isExplaining = plan && currentActionIndex < plan.actions.length;
  const currentAction = isExplaining ? plan.actions[currentActionIndex] : null;

  // A function to get all interactable elements and their context
  const getUiContext = () => {
    const elements = Array.from(document.querySelectorAll("[id]")).map((el) => ({
      id: el.id,
      type: el.tagName.toLowerCase(),
      label: el.getAttribute("aria-label") || el.innerText,
    }));
    return {
      page: "dashboard",
      elements,
      // In a real app, you would populate these from your state
      visiblePanels: ["main-dashboard", "crypto-watchlist"],
      selected: { id: "", text: "", imageUrl: "" },
    };
  };

  const handleExplain = async (userText) => {
    setIsLoading(true);
    setPlan(null);
    setCurrentActionIndex(0);

    const uiContext = getUiContext();

    try {
      const res = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userText,
          uiContext,
          userState: { mode: "curious", focus: 0.9 },
          prefs: { language: "en", tone: "cheerful" },
        }),
      });
      if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
      const data = await res.json();
      setPlan(data);
    } catch (error) {
      console.error("Failed to get explanation plan:", error);
      // Show a toast to the user
      alert(`Error: ${error.message}`);
    }

    setIsLoading(false);
  };

  const handleNextAction = () => {
    if (isExplaining) {
      setCurrentActionIndex(currentActionIndex + 1);
    }
  };

  // Auto-advance for non-interactive actions
  useEffect(() => {
    if (currentAction?.type === "wait" || currentAction?.type === "say") {
      const delay = currentAction.duration || 2000; // Default wait time
      const timer = setTimeout(handleNextAction, delay);
      return () => clearTimeout(timer);
    }
  }, [currentAction]);


  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Etherea</h1>
        <CandyButton id="explain-button" onClick={() => handleExplain("Explain this dashboard")}>
          {isLoading ? "Thinking..." : "Explain UI"}
        </CandyButton>
      </header>

      <main className="dashboard-grid">
        <CandyCard id="main-dashboard">
          <h2>Main Dashboard</h2>
          {/* Content would go here */}
        </CandyCard>
        <CandyCard id="crypto-watchlist">
          <h2>Crypto Watchlist</h2>
          {/* Content would go here */}
        </CandyCard>
        <CandyCard id="news-feed">
          <h2>News Feed</h2>
          {/* Content would go here */}
        </CandyCard>
      </main>

       {isExplaining && currentAction.type === 'spotlight' && (
        <CandySpotlightOverlay action={currentAction} onEnd={handleNextAction} />
      )}

      <div className="explainer-avatar">
         <AuroraRing isSpeaking={isExplaining} expression={plan?.expression} />
        <div className="avatar-bubble">
            {isExplaining ? plan.say : "Hi! How can I help?"}
        </div>
      </div>
    </div>
  );
};

export default App;
