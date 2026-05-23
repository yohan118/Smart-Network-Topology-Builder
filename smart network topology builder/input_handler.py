def ask_number(question):
    while True:
        answer = input(question)
        if answer.isdigit():
            number = int(answer)
            if number > 0:
                return number
            else:
                print("Please enter a number bigger than 0.")
        else:
            print("Please enter a valid whole number.")


def ask_yes_no(question):
    while True:
        answer = input(question).strip().lower()
        if answer == "yes" or answer == "y":
            return "yes"
        if answer == "no" or answer == "n":
            return "no"
        print("Please type yes or no.")


def ask_text(question):
    while True:
        answer = input(question).strip()
        if answer != "":
            return answer
        print("This cannot be empty.")


def normalize_name(name):
    cleaned = name.strip().lower()
    known = {}
    known["it"] = "IT"
    known["hr"] = "HR"
    known["finance"] = "Finance"
    known["management"] = "Management"
    known["servers"] = "Servers"
    known["server"] = "Servers"
    known["guest wifi"] = "Guest WiFi"
    known["guest"] = "Guest WiFi"
    known["guestwifi"] = "Guest WiFi"
    if cleaned in known:
        return known[cleaned]
    return name.strip().title()


def get_requirements():
    print("=========================================")
    print(" SMART NETWORK TOPOLOGY BUILDER - SETUP")
    print("=========================================")

    data = {}
    data["company"] = ask_text("Company name: ")
    dept_count = ask_number("How many departments? ")

    departments = []
    used_names = []
    i = 1
    while i <= dept_count:
        print("")
        print("Department " + str(i))
        name = ask_text("  Name: ")
        name = normalize_name(name)
        while name in used_names:
            print("  That name is already used. Pick another.")
            name = ask_text("  Name: ")
            name = normalize_name(name)
        used_names.append(name)
        users = ask_number("  How many users? ")
        dept = {}
        dept["name"] = name
        dept["users"] = users
        departments.append(dept)
        i = i + 1

    data["departments"] = departments
    data["branches"] = ask_number("How many branch offices (not counting HQ)? ")
    data["vpn"] = ask_yes_no("Need VPN between branches? (yes/no) ")
    data["guest"] = ask_yes_no("Need Guest WiFi? (yes/no) ")
    data["servers"] = ask_yes_no("Need a server room at HQ? (yes/no) ")

    return data


def sample_requirements():
    data = {}
    data["company"] = "TechCorp"
    data["departments"] = [
        {"name": "IT", "users": 30},
        {"name": "HR", "users": 50},
        {"name": "Finance", "users": 20},
        {"name": "Management", "users": 10},
    ]
    data["branches"] = 2
    data["vpn"] = "yes"
    data["guest"] = "yes"
    data["servers"] = "yes"
    return data
