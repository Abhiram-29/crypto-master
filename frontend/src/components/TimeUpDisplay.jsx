import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { logoutUser } from "../userSlice";

const TimeUpDisplay = () => {
  const timeLeft = useSelector((state) => state.user.time_left);
  const userId = useSelector((state) => state.user.user_id);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [showTimeUp, setShowTimeUp] = useState(false);
  const [finalCoins, setFinalCoins] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL;
  const API_KEY = import.meta.env.VITE_API_KEY;

  useEffect(() => {
    if (timeLeft <= 0 && !showTimeUp) {
      console.log("Time’s up!");
      setShowTimeUp(true);
      
      // Clear local storage when time is up
      localStorage.clear();  

      const sendEndSessionRequest = async () => {
        if (!userId) {
          console.error("Error: user_id is missing!");
          return;
        }

        const requestData = {
          user_id: userId,
          end_time: new Date().toISOString(),
        };

        console.log("Sending request:", requestData);

        try {
          const response = await fetch(`${API_URL}/end`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "API_KEY": API_KEY,
            },
            body: JSON.stringify(requestData),
          });

          const responseData = await response.json();
          console.log("Server Response:", responseData);

          if (!response.ok) {
            throw new Error(`HTTP Error! Status: ${response.status}, Message: ${responseData.message}`);
          }

          setFinalCoins(responseData["Final coin tally"] || 0);

          console.log("Session ended successfully");
        } catch (error) {
          console.error("Error ending session:", error);
        }
      };

      sendEndSessionRequest();
    }
  }, [timeLeft, userId, dispatch, showTimeUp]);

  const handleRestart = () => {
    dispatch(logoutUser()); // Reset user state only on Restart click
    setShowTimeUp(false); // Close the popup
    navigate("/"); // Redirect to login page
  };

  if (!showTimeUp) return null;

  return (
    <div className="time-up-overlay">
      <div className="time-up-content">
        <h2>Time’s Up!</h2>
        <p>Your session has expired.</p>
        <p>Final Coin Tally: <strong>{finalCoins !== null ? finalCoins : "Calculating..."}</strong></p>
        <button onClick={handleRestart} className="retry-btn">
          Restart
        </button>
      </div>
    </div>
  );
};

export default TimeUpDisplay;
