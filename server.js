import bcrypt from "bcryptjs";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import jwt from "jsonwebtoken";
import mysql from "mysql2/promise";

dotenv.config();

const app = express();
const port = Number(process.env.PORT || 5000);
const jwtSecret = process.env.JWT_SECRET;

if (!jwtSecret) {
  throw new Error("JWT_SECRET is required. Add it to .env before starting the server.");
}

const allowedOrigins = [
  "http://127.0.0.1:5174",
  "http://localhost:5174"
];

app.use(cors({ origin: allowedOrigins }));
app.use(express.json());

const pool = mysql.createPool({
  host: process.env.DB_HOST || "localhost",
  user: process.env.DB_USER || "root",
  password: process.env.DB_PASSWORD || "",
  database: process.env.DB_NAME || "fitness_trac",
  waitForConnections: true,
  connectionLimit: 10
});

const workoutPlan = [
  { day: "Monday", focus: "Back Strength", exercises: ["Deadlifts", "Pull-Ups", "Lat Pulldowns", "Bent Over Rows", "T-Bar Row"] },
  { day: "Tuesday", focus: "Chest Power", exercises: ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-Ups", "Cable Crossovers"] },
  { day: "Wednesday", focus: "Shoulders", exercises: ["Military Press", "Lateral Raise", "Front Raise", "Rear Delt Fly", "Arnold Press"] },
  { day: "Thursday", focus: "Biceps", exercises: ["Barbell Curls", "Hammer Curls", "Concentration Curls", "Cable Curls", "Preacher Curls"] },
  { day: "Friday", focus: "Triceps", exercises: ["Tricep Dips", "Skull Crushers", "Overhead Extension", "Tricep Pushdown", "Close Grip Bench Press"] },
  { day: "Saturday", focus: "Leg Day", exercises: ["Squats", "Lunges", "Leg Press", "Hamstring Curls", "Calf Raises"] },
  { day: "Sunday", focus: "Cardio", exercises: ["Running", "Cycling", "Jump Rope", "HIIT", "Swimming"] }
];

function auth(req, res, next) {
  const header = req.headers.authorization || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;

  if (!token) {
    return res.status(401).json({ message: "Authentication required." });
  }

  try {
    req.user = jwt.verify(token, jwtSecret);
    next();
  } catch {
    res.status(401).json({ message: "Session expired. Please login again." });
  }
}

function rangesFor(sex) {
  return sex === "female"
    ? { caloriesMin: 1800, caloriesMax: 2400, waterGoal: 2.7 }
    : { caloriesMin: 2400, caloriesMax: 3000, waterGoal: 3.7 };
}

function calorieMessage(calories, sex) {
  const range = rangesFor(sex);
  if (calories < range.caloriesMin) return "You are below today's recommended intake.";
  if (calories > range.caloriesMax) return "You are above today's recommended intake.";
  return "Your calories are in a healthy range today.";
}

function waterMessage(water, sex) {
  const range = rangesFor(sex);
  return Number(water) >= range.waterGoal ? "Hydration goal reached." : "Drink more water to hit your goal.";
}

function publicUser(user) {
  return {
    id: user.id,
    username: user.username,
    age: Number(user.age),
    weight: Number(user.weight),
    sex: user.sex,
    goal: user.goal
  };
}

function isValidGoal(goal) {
  return ["lose_weight", "maintain", "gain_muscle"].includes(goal);
}

function validateProfile({ username, password, age, weight, sex, goal }) {
  if (!username || String(username).trim().length < 3) return "Username must be at least 3 characters.";
  if (!password || String(password).length < 6) return "Password must be at least 6 characters.";
  if (!Number.isFinite(Number(age)) || Number(age) < 12 || Number(age) > 100) return "Age must be between 12 and 100.";
  if (!Number.isFinite(Number(weight)) || Number(weight) < 20 || Number(weight) > 300) return "Weight must be between 20 and 300 kg.";
  if (!["male", "female"].includes(sex)) return "Please select a valid sex.";
  if (!isValidGoal(goal)) return "Please select a valid goal.";
  return null;
}

app.get("/api/health", async (_req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ ok: true, database: "connected" });
  } catch {
    res.status(503).json({ ok: false, database: "unavailable" });
  }
});

app.post("/api/auth/register", async (req, res) => {
  const { username, password, age, weight, sex, goal = "maintain" } = req.body;
  const validationError = validateProfile({ username, password, age, weight, sex, goal });

  if (validationError) {
    return res.status(400).json({ message: validationError });
  }

  const passwordHash = await bcrypt.hash(password, 10);

  try {
    const [result] = await pool.execute(
      "INSERT INTO users (username, password_hash, age, weight, sex, goal) VALUES (?, ?, ?, ?, ?, ?)",
      [username.trim(), passwordHash, Number(age), Number(weight), sex, goal]
    );

    const user = { id: result.insertId, username: username.trim(), age, weight, sex, goal };
    const token = jwt.sign({ id: user.id, username: user.username }, jwtSecret, { expiresIn: "7d" });
    res.status(201).json({ token, user: publicUser(user) });
  } catch (error) {
    if (error.code === "ER_DUP_ENTRY") {
      return res.status(409).json({ message: "Username already exists." });
    }
    res.status(500).json({ message: "Registration failed." });
  }
});

app.post("/api/auth/login", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ message: "Username and password are required." });
  }

  const [rows] = await pool.execute("SELECT * FROM users WHERE username = ?", [username]);
  const user = rows[0];

  if (!user || !(await bcrypt.compare(password, user.password_hash))) {
    return res.status(401).json({ message: "Invalid username or password." });
  }

  const token = jwt.sign({ id: user.id, username: user.username }, jwtSecret, { expiresIn: "7d" });
  res.json({ token, user: publicUser(user) });
});

app.get("/api/me", auth, async (req, res) => {
  const [rows] = await pool.execute("SELECT id, username, age, weight, sex, goal FROM users WHERE id = ?", [req.user.id]);
  if (!rows[0]) return res.status(404).json({ message: "User not found." });
  res.json({ user: rows[0] });
});

app.get("/api/workouts", auth, (_req, res) => {
  res.json({ workoutPlan });
});

app.get("/api/intake/today", auth, async (req, res) => {
  const [users] = await pool.execute("SELECT sex FROM users WHERE id = ?", [req.user.id]);
  const [logs] = await pool.execute(
    "SELECT calories, water, log_date FROM intake_logs WHERE user_id = ? AND log_date = CURRENT_DATE",
    [req.user.id]
  );
  const sex = users[0]?.sex || "male";
  const log = logs[0] || { calories: 0, water: 0, log_date: new Date().toISOString().slice(0, 10) };

  res.json({
    log: {
      calories: Number(log.calories || 0),
      water: Number(log.water || 0),
      date: log.log_date
    },
    recommendations: {
      ...rangesFor(sex),
      calorieMessage: calorieMessage(Number(log.calories || 0), sex),
      waterMessage: waterMessage(Number(log.water || 0), sex)
    }
  });
});

app.put("/api/intake/today", auth, async (req, res) => {
  const calories = Number(req.body.calories || 0);
  const water = Number(req.body.water || 0);

  if (!Number.isFinite(calories) || calories < 0 || calories > 10000) {
    return res.status(400).json({ message: "Calories must be between 0 and 10000." });
  }

  if (!Number.isFinite(water) || water < 0 || water > 20) {
    return res.status(400).json({ message: "Water must be between 0 and 20 liters." });
  }

  await pool.execute(
    `INSERT INTO intake_logs (user_id, log_date, calories, water)
     VALUES (?, CURRENT_DATE, ?, ?)
     ON DUPLICATE KEY UPDATE calories = VALUES(calories), water = VALUES(water)`,
    [req.user.id, calories, water]
  );

  const [users] = await pool.execute("SELECT sex FROM users WHERE id = ?", [req.user.id]);
  const sex = users[0]?.sex || "male";

  res.json({
    log: { calories, water, date: new Date().toISOString().slice(0, 10) },
    recommendations: {
      ...rangesFor(sex),
      calorieMessage: calorieMessage(calories, sex),
      waterMessage: waterMessage(water, sex)
    }
  });
});

app.get("/api/intake/history", auth, async (req, res) => {
  const [rows] = await pool.execute(
    `SELECT log_date AS date, calories, water
     FROM intake_logs
     WHERE user_id = ?
     ORDER BY log_date DESC
     LIMIT 14`,
    [req.user.id]
  );

  res.json({
    history: rows.map((row) => ({
      date: row.date,
      calories: Number(row.calories || 0),
      water: Number(row.water || 0)
    }))
  });
});

app.listen(port, () => {
  console.log(`PulseFit API running on http://127.0.0.1:${port}`);
});
