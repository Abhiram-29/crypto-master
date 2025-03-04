import React, { useState, useEffect } from "react";
import QuestionPopup from "./QuestionPopup";
import { FaSpinner, FaCubes, FaLayerGroup, FaQuestion, FaLock, FaClock, FaCoins, FaCheck } from "react-icons/fa";
import { useSelector, useDispatch } from "react-redux";
import { Modal, Slider } from "antd";
import { setUser } from "../userSlice";
import { useNavigate } from "react-router-dom"; // Import navigate
import { logoutUser } from "../userSlice"; // Ensure this action exists in userSlice


const Questions = () => {
  const [questions, setQuestions] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [betAmount, setBetAmount] = useState(10);
  const [questionToOpen, setQuestionToOpen] = useState(null);
  const [isPlacingBet, setIsPlacingBet] = useState(false); // New state
  const [isEndGameModalOpen, setIsEndGameModalOpen] = useState(false);
  const [isWarningModalOpen, setIsWarningModalOpen] = useState(false); 
  const [warningMessage, setWarningMessage] = useState("");

  const navigate = useNavigate(); // Initialize navigatio

  const user = useSelector((state) => state.user);
  const timeLeft = user.time_left; 
  const coins = user.coins;
  const dispatch = useDispatch();
  const API_URL = import.meta.env.VITE_API_URL;
  const API_KEY = import.meta.env.VITE_API_KEY;

  // Function to fetch questions
  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/questions`, {
        method: "POST",
        headers: {
          accept: "application/json",
          "API_KEY": API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: user.user_id }),
      });

      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }

      const data = await response.json();
      if (data && data.questions) {
        setQuestions(data.questions);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error("Error fetching questions:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch questions when component mounts
  useEffect(() => {
    fetchQuestions();
  }, [user.user_id]);

  const handleQuestionClick = (question) => {
    if (question.status === "locked") {
      if (user.coins < (question.minimum_spend || 10)) {
        setWarningMessage(`Oops! 😲 You need at least ${question.minimum_spend || 10} coins to unlock this question. 
        Try solving other questions or earning more coins first! 🏆`);
        setIsWarningModalOpen(true);
        return;
      }
      setQuestionToOpen(question);
      setBetAmount(question.minimum_spend || 10);
      setIsModalOpen(true);
    } else if (["attempting", "solved", "wrong answer"].includes(question.status)) {
      setSelectedQuestion(question);
    }
  };
  
  

  const fetchUpdatedUser = async () => {
    try {
      const userResponse = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
          API_KEY: API_KEY,
        },
        body: JSON.stringify({ user_id: user.user_id }),
      });

      if (userResponse.ok) {
        const updatedUserData = await userResponse.json();
        dispatch(setUser(updatedUserData));
      }
    } catch (error) {
      console.error("Error fetching updated user data:", error);
    }
  };

  const handleModalConfirm = async () => {
    if (!questionToOpen) return;
  
    setIsPlacingBet(true); // Disable button and update text
  
    const requestData = {
      user_id: user.user_id,
      question_id: questionToOpen.question_id,
      bet_amt: betAmount,
      time_left: timeLeft,
    };
  
    try {
      const response = await fetch(`${API_URL}/questionStart`, {
        method: "POST",
        headers: {
          accept: "application/json",
          "API_KEY": API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }
  
      const responseData = await response.json();
  
      if (responseData.success) {
        dispatch(setUser({ ...user, coins: responseData.coins }));
        fetchUpdatedUser();
      }
  
      setIsModalOpen(false);
      setSelectedQuestion(questionToOpen);
      fetchQuestions(); // Refresh questions after unlocking
    } catch (error) {
      console.error("Error updating question status:", error);
    } finally {
      setIsPlacingBet(false); // Reset button state
    }
  };

  const generateMarks = (min, max) => {
    const stepSize = (max - min) / 4; // Divide into 5 points (including min and max)
    let marks = {};
  
    for (let i = 0; i <= 4; i++) {
      const value = Math.round(min + i * stepSize);
      marks[value] = `${value}`; // Assign labels to marks
    }
  
    return marks;
  };
  
  if (loading) {
    return (
      <div className="loading-screen">
        <FaSpinner className="loading-icon" />
        <p>Loading Questions...</p>
      </div>
    );
  }

  const handleEndGame = async () => {
    try {
      const response = await fetch(`${API_URL}/end`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "API_KEY": API_KEY,
        },
        body: JSON.stringify({
          user_id: user.user_id,
          end_time: new Date().toISOString(),
          coins: coins,
        }),
      });

      if (!response.ok) throw new Error(`HTTP Error! Status: ${response.status}`);
      const responseData = await response.json();
      console.log("End Game Response:", responseData);

      dispatch(logoutUser());
      navigate("/");
    } catch (error) {
      console.error("Error ending game session:", error);
    }
  };
  

  return (
    <div className="questions-page">
      <h1 className="page-title">Crypto Challenge Questions</h1>
      <div className="questions-grid">
        {questions.map((q, index) => (
          <div
            key={q._id || index}
            className={`question-card ${q.status || "locked"}`}
            onClick={() => handleQuestionClick(q)}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            {q.status === "locked" && (
              <div className="lock-overlay">
                <FaLock className="lock-icon" />
              </div>
            )}
            <div className="card-content">
              <h3 className="card-topic">
                <FaCubes className="topic-icon" />{q.topic}
              </h3>
              
              <div className="card-info-row">
                <div className="info-item">
                  <FaLayerGroup className="info-icon" />{q.difficulty}
                </div>
                <div className="info-item">
                  <FaQuestion className="info-icon" />{q.question_type}
                </div>
              </div>
              
              <div className="status-badge">
                {q.status === "locked" ? 
                  <FaLock className="status-icon" /> : 
                  q.status === "attempting" ? 
                    <FaClock className="status-icon" /> : 
                    <FaCheck className="status-icon" />
                }
                Status: {q.status}
              </div>
              
              <div className="profit-multiplier">
                <FaCoins className="multiplier-icon" />
                Profit Multiplier: {q.multiplier}x
              </div>
            </div>
          </div>
        ))}
      </div>

      <Modal
          title="Big Decision Time! 💰"
          open={isModalOpen}
          onOk={handleModalConfirm}
          onCancel={() => setIsModalOpen(false)}
          okText={isPlacingBet ? "Placing Bet... 🎲" : "Lock It In! 🚀"}
          cancelText="Nah, Changed My Mind"
          okButtonProps={{ disabled: isPlacingBet }} // Disable button when processing
        >
          <p>Alright, high roller! This question is locked. Ready to risk it for the biscuit? 🏆</p>
          <p>Choose your bet wisely… fortune favors the bold! 🔥</p>
          {questionToOpen && (
            <>
              <Slider 
                min={questionToOpen.minimum_spend || 10} 
                max={user.coins} 
                value={betAmount}
                onChange={(value) => setBetAmount(value)} 
                marks={generateMarks(questionToOpen.minimum_spend || 10, user.coins)}
                step={null}
              />
            <p>Bet Amount: <strong>{betAmount} coins</strong> </p>
        <p>Extra Earnings: <strong>{(betAmount * (questionToOpen.multiplier || 1)).toFixed(2)} coins</strong></p>

            </>
          )}
        </Modal>


      {selectedQuestion && (
        <QuestionPopup
          question={selectedQuestion}
          onClose={() => {
            setSelectedQuestion(null);
            fetchQuestions(); // Refresh questions when exiting
          }}
          userId={user.user_id}
          timeLeft={timeLeft}  
          betAmount={betAmount}
          fetchQuestions={fetchQuestions} // Pass function to refresh questions
        />
        
      )}
      <button 
        type="default"
        style={{ 
          backgroundColor: "#ff4d4f", 
          color: "white", 
          fontSize: "16px", 
          padding: "12px 24px", 
          borderRadius: "8px", 
          position: "fixed", 
          bottom: "20px", 
          left: "50%", 
          transform: "translateX(-50%)", // Centers it
          zIndex: 9999
        }}
        onClick={() => setIsEndGameModalOpen(true)}
      >
        End Game 🚪🏃‍♂️
      </button>

      <Modal
        title="Are you sure?"
        open={isEndGameModalOpen}
        onOk={handleEndGame}
        onCancel={() => setIsEndGameModalOpen(false)}
        okText="Yes, End Game"
        cancelText="Cancel"
      >
        <p>Ending the game will log you out and finalize your earnings. Are you sure you want to proceed?</p>
        <p>your Earnings till now {coins}</p>
      </Modal>

      <Modal
        title="Not Enough Coins! 🚨"
        open={isWarningModalOpen}
        onOk={() => setIsWarningModalOpen(false)}
        okText="Got it! 💰"
        cancelButtonProps={{ style: { display: "none" } }} // Hide cancel button
      >
        <p>{warningMessage}</p>
      </Modal>
    </div>
  );
};

export default Questions;