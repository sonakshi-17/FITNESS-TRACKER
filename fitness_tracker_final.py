
import mysql.connector
from getpass import getpass
from datetime import date

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="your_username",     # replace with your MySQL username
    password="your_password", # replace with your MySQL password
    database="fitness_tracker"
)
cursor = conn.cursor()

# ------------------ USER AUTH ------------------

def register():
    print("\n--- Register New User ---")
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    age = int(input("Enter age: "))
    weight = float(input("Enter weight (kg): "))
    sex = input("Enter sex (male/female): ").lower()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        print("Username already exists. Try logging in.")
        return None

    cursor.execute(
        "INSERT INTO users (username, password, age, weight, sex) VALUES (%s, %s, %s, %s, %s)",
        (username, password, age, weight, sex)
    )
    conn.commit()
    print("Registration successful!")
    return username

def login():
    print("\n--- Login ---")
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        print(f"\nWelcome back, {username}!")
        print("Your Details:")
        print(f"Age: {user[3]} | Weight: {user[4]}kg | Sex: {user[5]}")
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
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            show_workout_plan()
        elif choice == "2":
            calorie_tracker(user[0], user[5])
        elif choice == "3":
            water_intake_tracker(user[0], user[5])
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

# ------------------ WORKOUT ------------------

def show_workout_plan():
    workout_plan = {
        "Monday (Back Day)": ["Deadlifts", "Pull-Ups", "Lat Pulldowns", "Bent Over Rows", "T-Bar Row"],
        "Tuesday (Chest Day)": ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-Ups", "Cable Crossovers"],
        "Wednesday (Shoulders)": ["Military Press", "Lateral Raise", "Front Raise", "Rear Delt Fly", "Arnold Press"],
        "Thursday (Biceps)": ["Barbell Curls", "Hammer Curls", "Concentration Curls", "Cable Curls", "Preacher Curls"],
        "Friday (Triceps)": ["Tricep Dips", "Skull Crushers", "Overhead Extension", "Tricep Pushdown", "Close Grip Bench Press"],
        "Saturday (Leg Day)": ["Squats", "Lunges", "Leg Press", "Hamstring Curls", "Calf Raises"],
        "Sunday (Cardio)": ["Running", "Cycling", "Jump Rope", "HIIT", "Swimming"]
    }
    for day, exercises in workout_plan.items():
        print(f"\n{day}:")
        for ex in exercises:
            print(f"  - {ex}")

# ------------------ CALORIE ------------------

def calorie_tracker(user_id, sex):
    print("\n--- Calorie Tracker ---")
    cal = int(input("Enter today's calorie intake: "))

    cursor.execute("SELECT id FROM intake_logs WHERE user_id = %s AND date = %s", (user_id, date.today()))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE intake_logs SET calories = %s WHERE id = %s", (cal, existing[0]))
    else:
        cursor.execute("INSERT INTO intake_logs (user_id, calories) VALUES (%s, %s)", (user_id, cal))
    conn.commit()

    if sex == "female":
        print("Recommended: 1800–2400 calories/day")
        if cal < 1800:
            print("You should eat more.")
        elif cal > 2400:
            print("You may be overeating.")
        else:
            print("Your intake is within the healthy range.")
    else:
        print("Recommended: 2400–3000 calories/day")
        if cal < 2400:
            print("You should eat more.")
        elif cal > 3000:
            print("You may be overeating.")
        else:
            print("Your intake is within the healthy range.")

# ------------------ WATER ------------------

def water_intake_tracker(user_id, sex):
    print("\n--- Water Intake Tracker ---")
    water = float(input("Enter water consumed today (in liters): "))

    cursor.execute("SELECT id FROM intake_logs WHERE user_id = %s AND date = %s", (user_id, date.today()))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE intake_logs SET water = %s WHERE id = %s", (water, existing[0]))
    else:
        cursor.execute("INSERT INTO intake_logs (user_id, water) VALUES (%s, %s)", (user_id, water))
    conn.commit()

    if sex == "female":
        print("Recommended: 2.7 liters/day")
        if water < 2.7:
            print("Drink more water.")
        else:
            print("Great! You're hydrated.")
    else:
        print("Recommended: 3.7 liters/day")
        if water < 3.7:
            print("Drink more water.")
        else:
            print("Great! You're hydrated.")

# ------------------ MAIN ------------------

def main():
    print("Welcome to the Fitness Tracker!")
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
