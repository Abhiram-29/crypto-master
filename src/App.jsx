import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import React from "react";
import Loginpage from "./components/Loginpage";
import Questions from "./components/Questions";
import Start from "./components/Start";
import Navbar from "./components/Navbar";
import "./App.css";


function App() {
  
  return (
    <>
    <Navbar/>
      <Router>
      <Routes>
        <Route path="/" element={<Loginpage />} />
        <Route path="/start" element={<Start />} />
        <Route path="/questions" element={<Questions />} />
      </Routes>
    </Router>
    </>
  )
}

export default App
