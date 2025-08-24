from datetime import date, timedelta
import mysql.connector
from getpass import getpass
from tabulate import tabulate

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arora@6800",
    database="fitness_tracker"
)
cursor = conn.cursor()

# ------------------ USER AUTH ------------------

def register():
    print("\n--- Register New User ---")
    username = input("Enter username: ")
    password = input("Enter password: ")
    age = int(input("Enter age: "))
    weight = float(input("Enter weight (kg): "))
    height = float(input("Enter height (m): "))
    sex = input("Enter sex (male/female): ").lower()
    calorie_goal = int(input("Enter your daily calorie goal: "))
    water_goal = float(input("Enter your daily water intake goal (liters): "))

    bmi = weight / (height ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        print("Username already exists. Try logging in.")
        return None

    cursor.execute(
        "INSERT INTO users (username, password, age, weight, height, sex, calorie_goal, water_goal) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (username, password, age, weight, height, sex, calorie_goal, water_goal)
    )
    conn.commit()
    print(f"Registration successful! Your BMI is {bmi:.2f} ({category})")
    return username

def login():
    print("\n--- Login ---")
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        print(f"\nWelcome back, {username}!")
        print(f"Age: {user[3]} | Weight: {user[4]}kg | Height: {user[5]}m | Sex: {user[6]}")
        return user
    else:
        print("Invalid credentials.")
        return None

# ------------------ MENU ------------------

def show_menu(user):
    while True:
        print("\n--- Fitness Tracker Menu ---")
        print("1. Workout Plan")
        print("2. Calorie Tracker")
        print("3. Water Intake Tracker")
        print("4. View Past 7-Day Logs")
        print("5. View Weekly Progress Summary")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            show_workout_plan()
        elif choice == "2":
            calorie_tracker(user[0], user[7])
        elif choice == "3":
            water_intake_tracker(user[0], user[8])
        elif choice == "4":
            view_past_logs(user[0])
        elif choice == "5":
            show_progress(user[0], user[7], user[8])
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

# ------------------ WORKOUT PLAN ------------------

from tabulate import tabulate

def show_workout_plan():
    workout_plan = {
        "Monday": ["Deadlifts", "Pull-Ups", "Lat Pulldowns", "Bent Over Rows", "T-Bar Row"],
        "Tuesday": ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-Ups", "Cable Crossovers"],
        "Wednesday": ["Military Press", "Lateral Raise", "Front Raise", "Rear Delt Fly", "Arnold Press"],
        "Thursday": ["Barbell Curls", "Hammer Curls", "Concentration Curls", "Cable Curls", "Preacher Curls"],
        "Friday": ["Tricep Dips", "Skull Crushers", "Overhead Extension", "Tricep Pushdown", "Close Grip Bench Press"],
        "Saturday": ["Squats", "Lunges", "Leg Press", "Hamstring Curls", "Calf Raises"],
        "Sunday": ["Running", "Cycling", "Jump Rope", "HIIT", "Swimming"]
    }

    print("\n--- Workout Plan Menu ---")
    print("1. View full weekly plan")
    print("2. View plan for a specific day")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        headers = ["Day", "Exercise 1", "Exercise 2", "Exercise 3", "Exercise 4", "Exercise 5"]
        rows = [[day] + exercises for day, exercises in workout_plan.items()]
        print("\nWeekly Workout Plan:")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

    elif choice == "2":
        selected_day = input("Enter day (e.g., Monday): ").strip().capitalize()
        if selected_day in workout_plan:
            exercises = workout_plan[selected_day]
            print(f"\n{selected_day} Workout Plan:")
            print(tabulate([[ex] for ex in exercises], headers=[selected_day], tablefmt="grid"))
        else:
            print("Invalid day entered. Please try again.")
    else:
        print("Invalid choice. Returning to main menu.")



# ------------------ CALORIE TRACKER ------------------

def calorie_tracker(user_id, goal):
    print("\n--- Calorie Tracker ---")
    cal = int(input("Enter today's calorie intake: "))

    if goal is None:
        print("⚠️  Error: Calorie goal is not set for this user. Please update your profile.")
        return

    today = date.today()
    cursor.execute("SELECT id FROM intake_logs WHERE user_id = %s AND date = %s", (user_id, today))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE intake_logs SET calories = %s WHERE id = %s", (cal, existing[0]))
    else:
        cursor.execute("INSERT INTO intake_logs (user_id, calories, date) VALUES (%s, %s, %s)", (user_id, cal, today))
    conn.commit()

    print(f"Your goal: {goal} cal")
    if cal < goal:
        print("You are under your goal today.")
    elif cal > goal:
        print("You exceeded your goal today.")
    else:
        print("You met your goal exactly!")

# ------------------ WATER TRACKER ------------------

def water_intake_tracker(user_id, goal):
    print("\n--- Water Intake Tracker ---")
    water = float(input("Enter today's water intake (liters): "))
    today = date.today()

    cursor.execute("SELECT id FROM intake_logs WHERE user_id = %s AND date = %s", (user_id, today))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE intake_logs SET water = %s WHERE id = %s", (water, existing[0]))
    else:
        cursor.execute("INSERT INTO intake_logs (user_id, water, date) VALUES (%s, %s, %s)", (user_id, water, today))
    conn.commit()

    print(f"Your goal: {goal} liters")
    if water < goal:
        print("Drink more water!")
    else:
        print("Great job! You met your hydration goal.")

# ------------------ VIEW PAST LOGS ------------------

def view_past_logs(user_id):
    print("\n--- Past 7-Day Logs ---")
    week_ago = date.today() - timedelta(days=7)
    cursor.execute("SELECT date, calories, water FROM intake_logs WHERE user_id = %s AND date >= %s ORDER BY date DESC", (user_id, week_ago))
    logs = cursor.fetchall()

    if logs:
        headers = ["Date", "Calories (kcal)", "Water (liters)"]
        print(tabulate(logs, headers=headers, tablefmt="grid"))
    else:
        print("No logs found for the past 7 days.")

# ------------------ PROGRESS FEEDBACK ------------------

def show_progress(user_id, cal_goal, water_goal):
    print("\n--- Weekly Progress Summary ---")
    week_ago = date.today() - timedelta(days=7)
    cursor.execute("SELECT date, calories, water FROM intake_logs WHERE user_id = %s AND date >= %s", (user_id, week_ago))
    logs = cursor.fetchall()

    if not logs:
        print("No logs found for the past 7 days.")
        return

    headers = ["Date", "Calories", "Water"]
    print(tabulate(logs, headers=headers, tablefmt="grid"))

    cal_days = sum(1 for log in logs if log[1] and log[1] >= cal_goal)
    water_days = sum(1 for log in logs if log[2] and log[2] >= water_goal)

    print(f"\n✅ Calorie goal met on: {cal_days} day(s)")
    print(f"✅ Water goal met on: {water_days} day(s)")


# ------------------ MAIN ------------------

def main():
    print("Welcome to the Enhanced Fitness Tracker!")
    user = None

    while not user:
        print("\nAre you a new user?")
        print("1. Yes")
        print("2. No (Login)")
        choice = input("Enter choice: ")

        if choice == "1":
            username = register()
            if username:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
        elif choice == "2":
            user = login()
        else:
            print("Invalid option.")

    if user:
        show_menu(user)

if __name__ == "__main__":
    main()
