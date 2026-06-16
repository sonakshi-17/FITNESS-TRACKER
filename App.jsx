import { useEffect, useMemo, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

const emptyAuth = {
  username: "",
  password: "",
  age: "",
  weight: "",
  sex: "male",
  goal: "maintain"
};

function getStoredSession() {
  try {
    return JSON.parse(localStorage.getItem("pulsefit_session")) || null;
  } catch {
    return null;
  }
}

async function api(path, options = {}, token) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    }
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || "Something went wrong.");
  return data;
}

export default function App() {
  const [session, setSession] = useState(getStoredSession);
  const [mode, setMode] = useState("login");
  const [authForm, setAuthForm] = useState(emptyAuth);
  const [workouts, setWorkouts] = useState([]);
  const [intake, setIntake] = useState(null);
  const [history, setHistory] = useState([]);
  const [intakeForm, setIntakeForm] = useState({ calories: 0, water: 0 });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const token = session?.token;
  const user = session?.user;

  useEffect(() => {
    if (!session) return;
    localStorage.setItem("pulsefit_session", JSON.stringify(session));
  }, [session]);

  useEffect(() => {
    if (!token) return;

    Promise.all([
      api("/workouts", {}, token),
      api("/intake/today", {}, token),
      api("/intake/history", {}, token)
    ])
      .then(([workoutData, intakeData, historyData]) => {
        setWorkouts(workoutData.workoutPlan);
        setIntake(intakeData);
        setHistory(historyData.history);
        setIntakeForm({
          calories: intakeData.log.calories,
          water: intakeData.log.water
        });
      })
      .catch((error) => setMessage(error.message));
  }, [token]);

  const calorieProgress = useMemo(() => {
    if (!intake) return 0;
    return Math.min(100, Math.round((Number(intakeForm.calories) / intake.recommendations.caloriesMax) * 100));
  }, [intake, intakeForm.calories]);

  const waterProgress = useMemo(() => {
    if (!intake) return 0;
    return Math.min(100, Math.round((Number(intakeForm.water) / intake.recommendations.waterGoal) * 100));
  }, [intake, intakeForm.water]);

  async function submitAuth(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const path = mode === "login" ? "/auth/login" : "/auth/register";
      const payload = mode === "login"
        ? { username: authForm.username, password: authForm.password }
        : authForm;
      const data = await api(path, { method: "POST", body: JSON.stringify(payload) });
      setSession(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function saveIntake(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const data = await api(
        "/intake/today",
        { method: "PUT", body: JSON.stringify(intakeForm) },
        token
      );
      const historyData = await api("/intake/history", {}, token);
      setIntake(data);
      setHistory(historyData.history);
      setMessage("Today's log has been updated.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("pulsefit_session");
    setSession(null);
    setIntake(null);
    setHistory([]);
    setWorkouts([]);
  }

  if (!session) {
    return (
      <main className="auth-shell">
        <section className="brand-panel">
          <div className="brand-mark">PF</div>
          <p className="eyebrow">PulseFit OS</p>
          <h1>Train, track, hydrate, repeat.</h1>
          <p className="hero-copy">
            A modern fitness dashboard built from your original tracker, now ready for React, MySQL, and real users.
          </p>
          <div className="hero-stats">
            <span>7 day split</span>
            <span>Calories</span>
            <span>Water</span>
          </div>
        </section>

        <section className="auth-card">
          <div className="tabs">
            <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
            <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
          </div>

          <form onSubmit={submitAuth} className="form-grid">
            <label>
              Username
              <input value={authForm.username} onChange={(event) => setAuthForm({ ...authForm, username: event.target.value })} required />
            </label>
            <label>
              Password
              <input type="password" value={authForm.password} onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })} required />
            </label>

            {mode === "register" && (
              <>
                <label>
                  Age
                  <input type="number" min="12" value={authForm.age} onChange={(event) => setAuthForm({ ...authForm, age: event.target.value })} required />
                </label>
                <label>
                  Weight (kg)
                  <input type="number" min="20" step="0.1" value={authForm.weight} onChange={(event) => setAuthForm({ ...authForm, weight: event.target.value })} required />
                </label>
                <label>
                  Sex
                  <select value={authForm.sex} onChange={(event) => setAuthForm({ ...authForm, sex: event.target.value })}>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </label>
                <label>
                  Goal
                  <select value={authForm.goal} onChange={(event) => setAuthForm({ ...authForm, goal: event.target.value })}>
                    <option value="maintain">Maintain</option>
                    <option value="lose_weight">Lose weight</option>
                    <option value="gain_muscle">Gain muscle</option>
                  </select>
                </label>
              </>
            )}

            {message && <p className="notice">{message}</p>}
            <button className="primary-action" disabled={loading}>{loading ? "Please wait..." : mode === "login" ? "Enter dashboard" : "Create account"}</button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-row">
          <div className="brand-mark">PF</div>
          <div>
            <strong>PulseFit</strong>
            <span>Fitness command center</span>
          </div>
        </div>
        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#workouts">Workout plan</a>
          <a href="#nutrition">Nutrition</a>
        </nav>
        <button className="ghost-action" onClick={logout}>Logout</button>
      </aside>

      <section className="content" id="dashboard">
        <header className="topbar">
          <div>
            <p className="eyebrow">Welcome back</p>
            <h1>{user.username}</h1>
          </div>
          <div className="profile-pill">
            <span>{user.age} yrs</span>
            <span>{user.weight} kg</span>
            <span>{user.goal.replace("_", " ")}</span>
          </div>
        </header>

        <section className="metrics-grid" id="nutrition">
          <article className="metric-card calories">
            <p>Calories today</p>
            <h2>{intakeForm.calories || 0}</h2>
            <div className="progress"><span style={{ width: `${calorieProgress}%` }} /></div>
            <small>{intake?.recommendations.calorieMessage}</small>
          </article>
          <article className="metric-card water">
            <p>Water today</p>
            <h2>{intakeForm.water || 0}L</h2>
            <div className="progress"><span style={{ width: `${waterProgress}%` }} /></div>
            <small>{intake?.recommendations.waterMessage}</small>
          </article>
          <article className="metric-card target">
            <p>Recommended range</p>
            <h2>{intake?.recommendations.caloriesMin}-{intake?.recommendations.caloriesMax}</h2>
            <small>{intake?.recommendations.waterGoal}L water goal</small>
          </article>
        </section>

        <section className="tracker-panel">
          <div>
            <p className="eyebrow">Daily check-in</p>
            <h2>Update your intake</h2>
          </div>
          <form onSubmit={saveIntake} className="tracker-form">
            <label>
              Calories
              <input type="number" min="0" value={intakeForm.calories} onChange={(event) => setIntakeForm({ ...intakeForm, calories: event.target.value })} />
            </label>
            <label>
              Water liters
              <input type="number" min="0" step="0.1" value={intakeForm.water} onChange={(event) => setIntakeForm({ ...intakeForm, water: event.target.value })} />
            </label>
            <button className="primary-action" disabled={loading}>Save log</button>
          </form>
          {message && <p className="notice">{message}</p>}
        </section>

        <section className="history-section">
          <div className="section-heading">
            <p className="eyebrow">Progress log</p>
            <h2>Recent entries</h2>
          </div>
          <div className="history-table">
            <div className="history-row header">
              <span>Date</span>
              <span>Calories</span>
              <span>Water</span>
            </div>
            {history.length === 0 && (
              <div className="history-row empty">
                <span>No entries yet</span>
                <span>-</span>
                <span>-</span>
              </div>
            )}
            {history.map((entry) => (
              <div className="history-row" key={entry.date}>
                <span>{new Date(entry.date).toLocaleDateString()}</span>
                <strong>{entry.calories}</strong>
                <strong>{entry.water}L</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="workout-section" id="workouts">
          <div className="section-heading">
            <p className="eyebrow">Training split</p>
            <h2>This week's plan</h2>
          </div>
          <div className="workout-grid">
            {workouts.map((day) => (
              <article className="workout-card" key={day.day}>
                <span>{day.day}</span>
                <h3>{day.focus}</h3>
                <ul>
                  {day.exercises.map((exercise) => <li key={exercise}>{exercise}</li>)}
                </ul>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
