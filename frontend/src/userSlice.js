import { createSlice } from "@reduxjs/toolkit";

// Load initial state from localStorage
const loadState = () => {
  try {
    const serializedState = localStorage.getItem("userState");
    if (serializedState === null) {
      return {
        name: "",
        email_id: "",
        coins: 0,
        time_left: 30 * 60,
        timerStarted: false,
        isLoggedIn: false,
        user_id: "",
      };
    }
    return JSON.parse(serializedState);
  } catch (err) {
    console.error("Failed to load state from localStorage", err);
    return {
      name: "",
      email_id: "",
      coins: 0,
      time_left: 30 * 60,
      timerStarted: false,
      isLoggedIn: false,
      user_id: "",
    };
  }
};

// Save state to localStorage
const saveState = (state) => {
  try {
    const serializedState = JSON.stringify(state);
    localStorage.setItem("userState", serializedState);
  } catch (err) {
    console.error("Failed to save state to localStorage", err);
  }
};

const initialState = loadState();

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setUser: (state, action) => {
      const { time_left, ...userData } = action.payload;
      const updatedState = {
        ...state,
        ...userData,
        time_left: time_left !== undefined ? time_left : state.time_left, // Set time_left from API if available
        timerStarted: state.timerStarted, // Preserve timer state
      };
      saveState(updatedState);
      return updatedState;
    },
    logoutUser: () => {
      const resetState = {
        name: "",
        email_id: "",
        coins: 0,
        time_left: 30 * 60,
        timerStarted: false,
        isLoggedIn: false,
        user_id: "",
      };
      saveState(resetState);
      return resetState;
    },
    setTimeLeft: (state, action) => {
      state.time_left = action.payload;
      saveState(state);
    },
    startTimer: (state) => {
      state.timerStarted = true;
      saveState(state);
    },
  },
});

export const { setUser, logoutUser, setTimeLeft, startTimer } = userSlice.actions;
export default userSlice.reducer;
