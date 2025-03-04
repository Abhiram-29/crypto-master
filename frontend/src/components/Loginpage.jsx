import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setUser } from "../userSlice";
import { FaUser, FaSpinner, FaLock } from 'react-icons/fa';
import 'bootstrap/dist/css/bootstrap.min.css';

const LoginPage = () => {
  const [userId, setUserId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const API_URL = import.meta.env.VITE_API_URL;
  const API_KEY = import.meta.env.VITE_API_KEY;
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
          "accept": "application/json",
          "API_KEY": API_KEY,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: userId }),
      });

      const data = await response.json();

      if (data.message === "User not found") {
        throw new Error("Login failed. Please check your User ID.");
      }

      if (data.time_left === 0) {
        throw new Error("Your session has expired. Please try again later.");
      }

      dispatch(setUser(data));
      navigate("/start");

    } catch (error) {
      console.error("Error logging in:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-wrapper">
      <div className="background-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
        <div className="shape shape-4"></div>
      </div>

      <div className="login-container">
        <div className="glass-effect"></div>
        <div className="login-box">
          <div className="login-content">
            <div className="icon-container">
              <FaUser className="user-icon" />
            </div>
            <h1 className="login-title">Welcome Back</h1>
            
            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <div className="input-group">
                  <div className="input-icon">
                    <FaLock />
                  </div>
                  <input
                    type="text"
                    className={`form-input ${error ? 'error' : ''}`}
                    placeholder="Enter User ID"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    disabled={isLoading}
                  />
                  <div className="input-border"></div>
                </div>
                {error && <div className="error-message">{error}</div>}
              </div>
              
              <button 
                type="submit" 
                className="login-btn"
                disabled={isLoading || !userId.trim()}
              >
                {isLoading ? (
                  <>
                    <FaSpinner className="spinner" /> Processing...
                  </>
                ) : (
                  'Login'
                )}
                <span className="btn-glow"></span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
