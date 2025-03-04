import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import React, { useEffect } from "react";
import Loginpage from "./components/Loginpage";
import Questions from "./components/Questions";
import Start from "./components/Start";
import Navbar from "./components/Navbar";
import TimeUpDisplay from "./components/TimeUpDisplay";
import "./App.css";

function App() {
  useEffect(() => {
    // Disable right-click
    const disableRightClick = (event) => event.preventDefault();
    document.addEventListener("contextmenu", disableRightClick);

    // Disable keyboard shortcuts
    const disableKeys = (event) => {
      if (
        event.keyCode === 123 || // F12
        (event.ctrlKey && event.shiftKey && event.keyCode === 73) || // Ctrl+Shift+I
        (event.ctrlKey && event.shiftKey && event.keyCode === 74) || // Ctrl+Shift+J
        (event.ctrlKey && event.keyCode === 85) || // Ctrl+U
        (event.ctrlKey && event.keyCode === 83) || // Ctrl+S (Save Page)
        (event.ctrlKey && event.keyCode === 72) // Ctrl+H (History)
      ) {
        event.preventDefault();
      }
    };

    document.addEventListener("keydown", disableKeys);

    // Cleanup on component unmount
    return () => {
      document.removeEventListener("contextmenu", disableRightClick);
      document.removeEventListener("keydown", disableKeys);
    };
  }, []);

  return (
    <Router>
      <Navbar />
      <TimeUpDisplay />
      <Routes>
        <Route path="/" element={<Loginpage />} />
        <Route path="/start" element={<Start />} />
        <Route path="/questions" element={<Questions />} />
      </Routes>
    </Router>
  );
}

export default App;
