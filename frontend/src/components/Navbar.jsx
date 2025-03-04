import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { FaUser, FaCoins, FaClock, FaBars } from "react-icons/fa";
import { Button, Navbar as BootstrapNavbar, Container } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import { setTimeLeft } from "../userSlice";

const Navbar = () => {
  const user = useSelector((state) => state.user);
  const dispatch = useDispatch();
  const timeLeft = useSelector((state) => state.user.time_left);
  const timerStarted = useSelector((state) => state.user.timerStarted);
  const API_URL = import.meta.env.VITE_API_URL;
  const API_KEY = import.meta.env.VITE_API_KEY;

  useEffect(() => {
    let timer;
    if (timerStarted && timeLeft > 0) {
      timer = setInterval(() => {
        dispatch(setTimeLeft(timeLeft - 1));
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [timerStarted, timeLeft, dispatch]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
  };

  const updateTime = async () => {
    try {
      const response = await fetch(`${API_URL}/updateTime`, {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json",
          "API_KEY" : API_KEY
        },
        body: JSON.stringify({
          user_id: user.user_id || "--",
          time_left: timeLeft,
        }),
      });
      const data = await response.json();
    } catch (error) {
      console.error("Error updating time:", error);
    }
  };

  return (
    <BootstrapNavbar bg="dark" variant="dark" expand="lg" className="custom-navbar">
      <Container>
        <BootstrapNavbar.Brand className="brand-name">
          <span className="gradient-text">Crypto Masters</span>
        </BootstrapNavbar.Brand>

        <div className="navbar-toggle">
          <FaBars />
        </div>

        <div className="user-info-container">
          <div className="info-item">
            <div className="icon-wrapper">
              <FaUser className="icon" />
            </div>
            <div className="info-content">
              <span className="info-label">User ID</span>
              <span className="info-value">{user.user_id || "--"}</span>
            </div>
          </div>

          <div className="info-item">
            <div className="icon-wrapper">
              <FaUser className="icon" />
            </div>
            <div className="info-content">
              <span className="info-label">Username</span>
              <span className="info-value">{user.name || "--"}</span>
            </div>
          </div>

          <div className="info-item">
            <div className="icon-wrapper">
              <FaCoins className="icon" />
            </div>
            <div className="info-content">
              <span className="info-label">Coins Left</span>
              <span className="info-value">
                {user.coins !== undefined ? user.coins.toFixed(2) : "--"}
              </span>
            </div>
          </div>

          {timerStarted && (
            <div className="info-item">
              <div className="icon-wrapper">
                <FaClock className="icon" />
              </div>
              <div className="info-content">
                <span className="info-label">Time Left</span>
                <span className="info-value">{formatTime(timeLeft)}</span>
              </div>
            </div>
          )}
        </div>

        <Button 
          variant="primary" 
          onClick={updateTime} 
          className="update-time-btn"
          style={{
            background: "linear-gradient(45deg,rgb(107, 186, 255),rgb(40, 111, 218))",
            border: "none",
            borderRadius: "20px",
            margin: "10px",
            padding: "10px 20px",
            fontSize: "16px",
            fontWeight: "bold",
            transition: "0.3s ease",
          }}
          onMouseOver={(e) => e.target.style.opacity = "0.8"}
          onMouseOut={(e) => e.target.style.opacity = "1"}
        >
          Update Time
        </Button>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar;
