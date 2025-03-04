import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { FaPlay, FaRocket } from "react-icons/fa";
import { setTimeLeft, startTimer } from "../userSlice";

const Start = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const timerStarted = useSelector((state) => state.user.timerStarted);
  const timeLeft = useSelector((state) => state.user.time_left);

  useEffect(() => {
    let timer;
    if (timerStarted && timeLeft > 0) {
      timer = setInterval(() => {
        dispatch(setTimeLeft(timeLeft - 1));
      }, 1000);
    } else if (timeLeft === 0) {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [timerStarted, timeLeft, dispatch]);

  const handleClick = (e) => {
    e.preventDefault();
    dispatch(startTimer()); // Start the timer
    navigate("/questions");
  };

  return (
    <div className="start-container">
      <div className="start-content">
        <div className="title-section">
          <h1 className="start-title">
            <FaRocket className="title-icon" />
            Crypto Masters Challenge
          </h1>
          <p className="start-subtitle">Ready to test your knowledge?</p>
        </div>

        <div className="start-card">
          <div className="card-content">
            <h2>Welcome to the Challenge</h2>
            <p>Test your crypto knowledge and compete with others!</p>

            <button onClick={handleClick} className="start-button">
              Start Challenge
              <FaPlay className="button-icon" />
            </button>
          </div>
        </div>

        <div className="instructions">
          <h3>Instructions:</h3>
          <ul>
            <li>Each round lasts exactly 40 minutes.</li>
            <li>
              You can select a question of any difficulty level and place a bet using your coins. There is a minimum bet amount for each question based on the difficulty level.
            </li>
            <li>
              When selecting a question, you will see the topic, difficulty level, and multiplier.
            </li>
            <li>
              The full question will only be revealed after you place your bet.
            </li>
            <li>
              The reward is calculated using a multiplier (e.g., if the multiplier is 1.5 and you bet 100 coins, you will receive 150 coins upon success).
            </li>
            <li>
              You can leave a question before submitting an answer and attempt a different one. In this case, your bet amount will be deducted from your total coins, but you can return to the question later with the same bet in place.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Start;
