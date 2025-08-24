import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import date, timedelta
from tabulate import tabulate

# ---------- Database Connection ----------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arora@6800",
    database="fitness_tracker"
)
cursor = conn.cursor()

# ---------- Global State ----------
root = tk.Tk()
root.title("Fitness Tracker System")
root.geometry("400x400")
current_user = None

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

# ---------- GUI Screens ----------

def main_menu():
    clear_window()
    tk.Label(root, text="Fitness Tracker", font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="Login", width=25, command=login_screen).pack(pady=10)
    tk.Button(root, text="Register", width=25, command=register_screen).pack(pady=10)
    tk.Button(root, text="Exit", width=25, command=exit_app).pack(pady=10)

def exit_app():
    conn.close()
    root.quit()

def login_screen():
    clear_window()
    tk.Label(root, text="Login", font=("Arial", 14)).pack(pady=10)
    tk.Label(root, text="Username").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()
    tk.Label(root, text="Password").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def do_login():
        global current_user
        username = username_entry.get()
        password = password_entry.get()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            current_user = user
            messagebox.showinfo("Success", f"Welcome {username}")
            dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    tk.Button(root, text="Login", command=do_login).pack(pady=10)
    tk.Button(root, text="Back", command=main_menu).pack()

def register_screen():
    clear_window()
    tk.Label(root, text="Register", font=("Arial", 14)).pack(pady=10)
    fields = ["Username", "Password", "Age", "Weight (kg)", "Height (m)", "Sex", "Calorie Goal", "Water Goal (L)"]
    entries = []

    for f in fields:
        tk.Label(root, text=f).pack()
        entry = tk.Entry(root, show="*" if f == "Password" else None)
        entry.pack()
        entries.append(entry)

    def do_register():
        data = [e.get() for e in entries]
        if "" in data:
            messagebox.showerror("Error", "All fields required")
            return

        try:
            username, password, age, weight, height, sex, cal_goal, water_goal = data
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username exists")
                return

            bmi = float(weight) / (float(height) ** 2)
            cursor.execute("""
                INSERT INTO users (username, password, age, weight, height, sex, calorie_goal, water_goal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, age, weight, height, sex.lower(), cal_goal, water_goal))
            conn.commit()
            messagebox.showinfo("Success", f"Registered! Your BMI: {bmi:.2f}")
            main_menu()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Register", command=do_register).pack(pady=10)
    tk.Button(root, text="Back", command=main_menu).pack()

def dashboard():
    clear_window()
    tk.Label(root, text=f"Welcome {current_user[1]}", font=("Arial", 14)).pack(pady=5)

    # Show user details
    age = current_user[3]
    weight = current_user[4]
    height = current_user[5]
    sex = current_user[6]
    calorie_goal = current_user[7]
    water_goal = current_user[8]

    tk.Label(root, text=f"Age: {age} | Weight: {weight} kg | Height: {height} m").pack()
    tk.Label(root, text=f"Sex: {str(sex).capitalize()} | Calorie Goal: {calorie_goal} kcal | Water Goal: {water_goal} L").pack(pady=5)


    # Action buttons
    tk.Button(root, text="Log Calorie Intake", width=30, command=calorie_screen).pack(pady=5)
    tk.Button(root, text="Log Water Intake", width=30, command=water_screen).pack(pady=5)
    tk.Button(root, text="View Workout Plan", width=30, command=workout_plan).pack(pady=5)
    tk.Button(root, text="View 7-Day Logs", width=30, command=view_logs).pack(pady=5)
    tk.Button(root, text="Weekly Progress", width=30, command=view_progress).pack(pady=5)
    tk.Button(root, text="Logout", width=30, command=main_menu).pack(pady=10)


# ---------- Features ----------

def calorie_screen():
    clear_window()
    tk.Label(root, text="Calorie Tracker", font=("Arial", 14)).pack(pady=10)
    tk.Label(root, text="Calories consumed today:").pack()
    entry = tk.Entry(root)
    entry.pack()

    def submit():
        try:
            val = int(entry.get())
            today = date.today()
            cursor.execute("SELECT id FROM intake_logs WHERE user_id=%s AND date=%s", (current_user[0], today))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE intake_logs SET calories=%s WHERE id=%s", (val, row[0]))
            else:
                cursor.execute("INSERT INTO intake_logs (user_id, calories, date) VALUES (%s, %s, %s)",
                               (current_user[0], val, today))
            conn.commit()
            goal = current_user[7]
            msg = "Goal met!" if val == goal else "Under goal" if val < goal else "Over goal"
            messagebox.showinfo("Result", msg)
            dashboard()
        except:
            messagebox.showerror("Error", "Enter a valid number")

    tk.Button(root, text="Submit", command=submit).pack(pady=5)
    tk.Button(root, text="Back", command=dashboard).pack()

def water_screen():
    clear_window()
    tk.Label(root, text="Water Tracker", font=("Arial", 14)).pack(pady=10)
    tk.Label(root, text="Water intake today (L):").pack()
    entry = tk.Entry(root)
    entry.pack()

    def submit():
        try:
            val = float(entry.get())
            today = date.today()
            cursor.execute("SELECT id FROM intake_logs WHERE user_id=%s AND date=%s", (current_user[0], today))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE intake_logs SET water=%s WHERE id=%s", (val, row[0]))
            else:
                cursor.execute("INSERT INTO intake_logs (user_id, water, date) VALUES (%s, %s, %s)",
                               (current_user[0], val, today))
            conn.commit()
            goal = current_user[8]
            msg = "Hydration goal met!" if val >= goal else "Drink more water"
            messagebox.showinfo("Result", msg)
            dashboard()
        except:
            messagebox.showerror("Error", "Enter a valid number")

    tk.Button(root, text="Submit", command=submit).pack(pady=5)
    tk.Button(root, text="Back", command=dashboard).pack()

def workout_plan():
    clear_window()
    plan = {
        "Monday": ["Deadlifts", "Pull-Ups", "Lat Pulldowns", "Bent Over Rows", "T-Bar Row"],
        "Tuesday": ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-Ups", "Cable Crossovers"],
        "Wednesday": ["Military Press", "Lateral Raise", "Front Raise", "Rear Delt Fly", "Arnold Press"],
        "Thursday": ["Barbell Curls", "Hammer Curls", "Concentration Curls", "Cable Curls", "Preacher Curls"],
        "Friday": ["Tricep Dips", "Skull Crushers", "Overhead Extension", "Tricep Pushdown", "Close Grip Bench Press"],
        "Saturday": ["Squats", "Lunges", "Leg Press", "Hamstring Curls", "Calf Raises"],
        "Sunday": ["Running", "Cycling", "Jump Rope", "HIIT", "Swimming"]

    }

    tk.Label(root, text="Workout Plan", font=("Arial", 14)).pack(pady=10)
    for day, exs in plan.items():
        tk.Label(root, text=f"{day}: {', '.join(exs)}").pack()

    tk.Button(root, text="Back", command=dashboard).pack(pady=10)

def view_logs():
    clear_window()
    tk.Label(root, text="Past 7-Day Logs", font=("Arial", 14)).pack(pady=10)
    week_ago = date.today() - timedelta(days=7)
    cursor.execute("SELECT date, calories, water FROM intake_logs WHERE user_id=%s AND date >= %s ORDER BY date DESC",
                   (current_user[0], week_ago))
    logs = cursor.fetchall()
    if logs:
        for log in logs:
            tk.Label(root, text=f"{log[0]} | Calories: {log[1]} | Water: {log[2]}L").pack()
    else:
        tk.Label(root, text="No data found").pack()

    tk.Button(root, text="Back", command=dashboard).pack(pady=10)

def view_progress():
    clear_window()
    tk.Label(root, text="Weekly Progress", font=("Arial", 14)).pack(pady=10)
    week_ago = date.today() - timedelta(days=7)
    cursor.execute("SELECT calories, water FROM intake_logs WHERE user_id=%s AND date >= %s",
                   (current_user[0], week_ago))
    logs = cursor.fetchall()

    if logs:
        cal_met = sum(1 for l in logs if l[0] and l[0] >= current_user[7])
        water_met = sum(1 for l in logs if l[1] and l[1] >= current_user[8])
        tk.Label(root, text=f"✅ Calorie goal met on {cal_met} day(s)").pack()
        tk.Label(root, text=f"✅ Water goal met on {water_met} day(s)").pack()
    else:
        tk.Label(root, text="No data available").pack()

    tk.Button(root, text="Back", command=dashboard).pack(pady=10)

# ---------- Start App ----------
main_menu()
root.mainloop()
