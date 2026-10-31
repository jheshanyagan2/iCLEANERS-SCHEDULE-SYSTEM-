from datetime import datetime

users = []
schedules = []
attendance = []
tasks = []
workdays = []

# ─── Pre-loaded list of rooms ────────────────────────────────────────────────
rooms = [
    "MsRoom 101",
    "MSRoom 102",
    "MSRoom 103",
    "MWRoom 201",
    "MWRoom 202",
    "Room 203",
    "Room 301",
    "Lobby",
    "Library",
    "basement",
    "b"
]

SHIFTS = ["Morning", "Afternoon"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]


def find_user(username):
    for u in users:
        if u["username"] == username:
            return u
    return None


def ask(label, validator=None):
    while True:
        v = input(label + " (0 to cancel): ").strip()
        if v == "0":
            return None
        if validator:
            err = validator(v)
            if err:
                print("  ! " + err)
                continue
        return v


def pick(options, title):
    while True:
        print("\n" + title)
        for i in range(len(options)):
            print(" ", i + 1, "-", options[i])
        c = input("Choose (0 to cancel): ").strip()
        if c == "0":
            return None
        if c.isdigit() and 1 <= int(c) <= len(options):
            return options[int(c) - 1]
        print("  ! Invalid choice")


def ask_time(label="Time", allow_skip=False):
    now = datetime.now().strftime("%H:%M")
    hint = "0 to skip" if allow_skip else "0 to cancel"
    while True:
        v = input(label + " [Enter = " + now + "] (" + hint + "): ").strip()
        if v == "0":
            return None
        if v == "":
            return now
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            print("  ! Use HH:MM (e.g. " + now + ").")


def not_empty(v):
    if v == "":
        return "Cannot be empty."


def unique_username(v):
    if v == "":
        return "Cannot be empty."
    if find_user(v):
        return "Username already exists."


def long_password(v):
    if len(v) < 4:
        return "Password must be at least 4 characters."


def valid_time(v):
    try:
        datetime.strptime(v, "%H:%M")
        return None
    except ValueError:
        return "Use HH:MM (e.g. 07:00)."

def login(role):
    print("\n=== " + role.upper() + " LOGIN (0 to cancel) ===")
    while True:
        username = ask(role.capitalize() + " username")
        if username is None:
            return None
        user = find_user(username)
        if user is None:
            print("  ! Username not found. Try again.\n")
            continue
        if user["role"] != role:
            print("  ! This account is not a " + role + ". Try again.\n")
            continue
        while True:
            password = ask("Password")
            if password is None:
                return None
            if user["password"] == password:
                print("  ✓ Welcome,", user["name"])
                return user
            print("  ! Wrong password. Try again.\n")


# ─── Auto Room Assignment ────────────────────────────────────────────────────

def find_available_room(day, shift):
    """Return the first room not used by any schedule on that day+shift."""
    used = set()
    for s in schedules:
        if s["day"] == day and s["shift"] == shift:
            used.add(s.get("room"))
    for r in rooms:
        if r not in used:
            return r
    return None


# ─── Workdays ────────────────────────────────────────────────────────────────

def get_workdays(username):
    for w in workdays:
        if w["username"] == username:
            return w["days"]
    return []


def set_workdays(username, days):
    for w in workdays:
        if w["username"] == username:
            w["days"] = days
            return
    workdays.append({"username": username, "days": days})


def show_days(days):
    if not days:
        print("    (no days assigned)")
        return
    for i in range(len(days)):
        print("    " + str(i + 1) + ". " + days[i])


def manage_workdays():
    print("\n=== MANAGE WORKDAYS ===")
    user = select_cleaner()
    if user is None:
        return

    chosen = list(get_workdays(user["username"]))
    print("\n  iCleaner: " + user["name"])

    while True:
        print("\n  Workdays for " + user["name"] + ":")
        show_days(chosen)

        print("\n  What do you want to do?")
        print("   1 - Add a day")
        print("   2 - Remove a day")
        print("   0 - Save and finish")
        c = input("  Choose: ").strip()

        if c == "1":
            remaining = [d for d in DAYS if d not in chosen]
            if not remaining:
                print("  ! All 7 days are already added.")
                continue
            d = pick(remaining, "ADD WHICH DAY?")
            if d is not None:
                chosen.append(d)
                print("  ✓ Added: " + d)

        elif c == "2":
            if not chosen:
                print("  ! There are no days to remove.")
                continue
            print("\n  Which day do you want to remove?")
            show_days(chosen)
            i = ask("  Day number",
                    lambda v: None if (v.isdigit()
                                       and 1 <= int(v) <= len(chosen))
                              else "Invalid number.")
            if i is None:
                continue
            removed = chosen[int(i) - 1]
            chosen.remove(removed)
            print("  ✓ Removed: " + removed)

        elif c == "0":
            set_workdays(user["username"], chosen)
            print("\n  ✓ Saved workdays for " + user["name"] + ":")
            show_days(chosen)
            return

        else:
            print("  ! Invalid choice. Please type 1, 2, or 0.")


def view_workdays():
    cleaners = [u for u in users if u["role"] == "iCleaner"]
    if not cleaners:
        print("  No iCleaners in the system yet.")
        return

    print("\n  === WORKDAYS BY CLEANER ===")
    print("  " + "-" * 72)
    print("  #   Cleaner Name         Username         Workdays")
    print("  " + "-" * 72)
    for i in range(len(cleaners)):
        u = cleaners[i]
        days = get_workdays(u["username"])
        day_str = ", ".join(days) if days else "(none)"
        print("  " + str(i + 1).ljust(3)
              + u["name"].ljust(21)
              + u["username"].ljust(16)
              + day_str)
    print("  " + "-" * 72)


# ─── Rooms ───────────────────────────────────────────────────────────────────

def add_room():
    print("\n=== ADD ROOM ===")
    name = ask("Room name (e.g. Room 101, Conference Room)", not_empty)
    if name is None:
        return
    if name in rooms:
        print("  ! This room already exists.")
        return
    rooms.append(name)
    print("  ✓ Room added: " + name)


def view_rooms():
    if not rooms:
        print("  No rooms yet.")
        return
    print("\n  #   Room")
    print("  " + "-" * 40)
    for i in range(len(rooms)):
        print("  " + str(i + 1).ljust(3) + rooms[i])


def delete_room():
    view_rooms()
    if not rooms:
        return

    i = ask("Room # to delete",
            lambda v: None if (v.isdigit() and 1 <= int(v) <= len(rooms))
                      else "Invalid number.")
    if i is None:
        return

    target = rooms[int(i) - 1]

    for s in schedules:
        if s.get("room") == target:
            print("  ! Cannot delete: this room is used by a schedule.")
            return

    rooms.remove(target)
    print("  ✓ Room deleted: " + target)


# ─── Users ───────────────────────────────────────────────────────────────────

def admin_add_user():
    print("\n=== CREATE NEW ACCOUNT ===")
    name = ask("Full name", not_empty)
    if name is None:
        return
    username = ask("Username", unique_username)
    if username is None:
        return
    password = ask("Password", long_password)
    if password is None:
        return
    role = pick(["iCleaner", "admin"], "ROLE")
    if role is None:
        return

    users.append({"name": name, "username": username,
                  "password": password, "role": role})

    if role == "iCleaner":
        workdays.append({"username": username, "days": []})

    print("  ✓ " + role.capitalize() + " account created for " + name + ".")
    print("    username:", username, "| password:", password)


def view_users():
    if not users:
        print("  No users.")
        return
    print("\n  #   Name                 Username         Role")
    print("  " + "-" * 55)
    for i in range(len(users)):
        u = users[i]
        print("  " + str(i + 1).ljust(3) + u["name"].ljust(21)
              + u["username"].ljust(16) + u["role"])


def delete_user(admin):
    view_users()
    if not users:
        return

    i = ask("User # to delete",
            lambda v: None if (v.isdigit() and 1 <= int(v) <= len(users))
                      else "Invalid number.")
    if i is None:
        return

    t = users[int(i) - 1]
    if t["username"] == admin["username"]:
        print("  ! You cannot delete your own account.")
        return
    if t["role"] == "admin":
        if len([u for u in users if u["role"] == "admin"]) <= 1:
            print("  ! Cannot delete the last admin.")
            return

    while True:
        c = input("Delete " + t["name"] + "? (yes/no, 0 to cancel): ").strip().lower()
        if c == "0" or c == "no":
            print("  Cancelled.")
            return
        if c == "yes":
            break
        print("  ! Please type yes or no.")

    global schedules, attendance, tasks, workdays
    schedules = [s for s in schedules if s["username"] != t["username"]]
    attendance = [a for a in attendance if a["username"] != t["username"]]
    tasks = [k for k in tasks if k["username"] != t["username"]]
    workdays = [w for w in workdays if w["username"] != t["username"]]
    users.remove(t)
    print("  ✓ User and related records deleted.")


# ─── Schedules ───────────────────────────────────────────────────────────────

def has_conflict(username, start, end, day):
    for s in schedules:
        if s["day"] != day:
            continue
        if not (start < s["end"] and end > s["start"]):
            continue
        if s["username"] == username:
            return True
    return False


def select_cleaner():
    cleaners = [u for u in users if u["role"] == "iCleaner"]
    if not cleaners:
        print("  ! No iCleaners in the system yet.")
        print("    Please create an iCleaner account first (Users → Create account).")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    print("\n=== iCLEANERS (today: " + today + ") ===")
    for i in range(len(cleaners)):
        u = cleaners[i]
        rec = find_attendance(u["username"], today)
        wd = get_workdays(u["username"])
        print(" ", i + 1, "-", u["name"],
              "(" + u["username"] + ")", "| today:",
              rec["status"] if rec else "—",
              "| workdays:", ", ".join(wd) if wd else "(none)")

    c = ask("Choose iCleaner number",
            lambda v: None if (v.isdigit() and 1 <= int(v) <= len(cleaners))
                      else "Invalid number.")
    if c is None:
        return None
    return cleaners[int(c) - 1]


def add_schedule():
    user = select_cleaner()
    if user is None:
        return

    wd = get_workdays(user["username"])
    if not wd:
        print("  ! " + user["name"] + " has no workdays assigned.")
        print("    Please set workdays first (Workdays → Manage).")
        return

    if not rooms:
        print("  ! No rooms available.")
        print("    Please add a room first (Rooms → Add room).")
        return

    shift = pick(SHIFTS, "SHIFTS")
    if shift is None:
        return

    while True:
        start = ask("Start time", valid_time)
        if start is None:
            return
        end = ask("End time", valid_time)
        if end is None:
            return
        if end > start:
            break
        print("  ! End time must be after start time.\n")

    chosen = []
    while True:
        day = pick(wd, "ADD A DAY (only workdays shown, 0 to finish)")
        if day is None:
            break
        if day in chosen:
            print("  ! Day already added.")
        else:
            chosen.append(day)
    if not chosen:
        print("  ! No days chosen.")
        return

    for day in chosen:
        if has_conflict(user["username"], start, end, day):
            print("  ! Conflict on", day, "for " + user["name"] + " - skipped.")
            continue

        room = find_available_room(day, shift)
        if room is None:
            print("  ! No available room on", day, shift, "- skipped.")
            continue

        schedules.append({"username": user["username"],
                          "room": room,
                          "shift": shift, "start": start,
                          "end": end, "day": day})
        tasks.append({
            "username": user["username"],
            "description": "General Cleaning",
            "room": room,
            "day": day,
            "done": False
        })
        print("  ✓ Added:", day, "|", shift, "→", user["name"],
              "| Room auto-assigned: " + room, "(Task auto-created)")


def auto_assign_present_cleaners():
    today_str = datetime.now().strftime("%Y-%m-%d")

    present = []
    for a in attendance:
        if a["date"] == today_str and a["status"] in ("Present", "Late"):
            u = find_user(a["username"])
            if u is not None and u["role"] == "iCleaner":
                present.append(u["username"])

    if not present:
        return 0

    covered = set()
    for s in schedules:
        covered.add((s["day"], s["shift"]))

    shift_times = {"Morning": ("07:00", "12:00"),
                   "Afternoon": ("13:00", "18:00")}

    newly_assigned = 0
    rotate = list(present)
    for day in DAYS:
        for shift in SHIFTS:
            if (day, shift) in covered:
                continue
            start, end = shift_times[shift]
            room = find_available_room(day, shift)
            if room is None:
                continue
            for _ in range(len(rotate)):
                cand = rotate[0]
                rotate.append(rotate.pop(0))
                if day not in get_workdays(cand):
                    continue
                if not has_conflict(cand, start, end, day):
                    schedules.append({
                        "username": cand,
                        "room": room,
                        "shift": shift, "start": start, "end": end,
                        "day": day,
                    })
                    tasks.append({
                        "username": cand,
                        "description": "General Cleaning",
                        "room": room,
                        "day": day,
                        "done": False
                    })
                    covered.add((day, shift))
                    newly_assigned += 1
                    break
    return newly_assigned


def view_schedules(username=None):
    if username is None:
        added = auto_assign_present_cleaners()
        if added > 0:
            print("\n  ✓ Auto-assigned " + str(added)
                  + " slot(s) to today's present iCleaners.")

    shown = [s for s in schedules
             if username is None or s["username"] == username]

    if not shown and username is not None:
        print("  No schedules assigned to you yet.")
        return shown

    if username is None:
        covered_set = set()
        for s in schedules:
            covered_set.add((s["day"], s["shift"]))

        total_combos = len(DAYS) * len(SHIFTS)

        taken = []
        for day in DAYS:
            for shift in SHIFTS:
                if (day, shift) in covered_set:
                    taken.append((day, shift))

        free = []
        for day in DAYS:
            for shift in SHIFTS:
                if (day, shift) not in covered_set:
                    free.append((day, shift))

        print("\n  === SCHEDULE OVERVIEW ===")
        print("  " + "-" * 80)
        print("  " + "Day".ljust(12) + "Shift".ljust(12)
              + "Cleaner".ljust(22) + "Room".ljust(20) + "Status")
        print("  " + "-" * 80)
        for day in DAYS:
            for shift in SHIFTS:
                if (day, shift) in covered_set:
                    found_cleaner = "—"
                    found_room = "—"
                    for s in schedules:
                        if s["day"] == day and s["shift"] == shift:
                            u = find_user(s["username"])
                            found_cleaner = u["name"] if u else s["username"]
                            found_room = s.get("room", "—")
                            break
                    print("  " + day.ljust(11) + " "
                          + shift.ljust(11) + " "
                          + found_cleaner.ljust(21) + " "
                          + found_room.ljust(19) + " ✓ Taken")
                else:
                    print("  " + day.ljust(11) + " "
                          + shift.ljust(11) + " "
                          + "—".ljust(21) + " "
                          + "—".ljust(19) + " ○ Free")
        print("  " + "-" * 80)

        print("\n  Summary: " + str(len(taken)) + " taken  |  "
              + str(len(free)) + " free  |  " + str(total_combos) + " total")
        print("  Rooms: " + (", ".join(rooms) if rooms else "(none)"))

    return shown


def delete_schedule():
    shown = view_schedules()
    if not shown:
        return
    i = ask("Number to delete (from the cleaner's own list, not taken view)",
            lambda v: None if (v.isdigit() and 1 <= int(v) <= len(shown))
                      else "Invalid number.")
    if i is None:
        return
    s = shown[int(i) - 1]

    global tasks
    tasks = [t for t in tasks
             if not (t["username"] == s["username"]
                     and t["day"] == s["day"]
                     and t.get("room") == s.get("room"))]

    schedules.remove(s)
    print("  ✓ Schedule and its linked task deleted.")
    print("    Room '" + s.get("room", "—") + "' is now available again.")


# ─── Attendance ──────────────────────────────────────────────────────────────

def find_attendance(username, date):
    for a in attendance:
        if a["username"] == username and a["date"] == date:
            return a
    return None


def mark_attendance(admin):
    print("\n=== MARK ATTENDANCE (TODAY) ===")
    cleaner = select_cleaner()
    if cleaner is None:
        return

    date = datetime.now().strftime("%Y-%m-%d")
    existing = find_attendance(cleaner["username"], date)

    print("\n  iCleaner:", cleaner["name"])
    print("  Date    :", date)
    if existing:
        print("  Current :", existing["status"], "- will update if new status chosen")

    status = pick(["Present", "Late", "Absent", "On leave"], "STATUS")
    if status is None:
        return

    time_in = time_out = None
    if status in ("Present", "Late"):
        while True:
            time_in = ask_time("Time in")
            if time_in is None:
                return
            time_out = ask_time("Time out", allow_skip=True)
            if time_out is None or time_out > time_in:
                break
            print("  ! Time out must be after time in.\n")

    rec = {"username": cleaner["username"], "date": date, "status": status,
           "time_in": time_in, "time_out": time_out,
           "marked_by": admin["username"]}

    if existing:
        existing.update(rec)
        print("  ✓ Updated:", cleaner["name"], "→", status)
    else:
        attendance.append(rec)
        print("  ✓ Recorded:", cleaner["name"], "→", status)


def view_attendance():
    if not attendance:
        print("  No attendance records.")
        return
    print("\n  Date        | iCleaner             | Status   | In    | Out   | By")
    print("  " + "-" * 78)
    for a in attendance:
        u = find_user(a["username"])
        print(" ", a["date"], "|",
              (u["name"] if u else a["username"]).ljust(20), "|",
              a["status"].ljust(8), "|",
              (a.get("time_in") or "-").ljust(5), "|",
              (a.get("time_out") or "-").ljust(5), "|",
              a.get("marked_by", "-"))


def my_attendance(user):
    mine = [a for a in attendance if a["username"] == user["username"]]
    if not mine:
        print("  No attendance records yet.")
        return
    print("\n  My attendance:")
    print("  " + "-" * 55)
    print("  Date        | Status   | In    | Out")
    print("  " + "-" * 55)
    for a in mine:
        print(" ", a["date"], "|", a["status"].ljust(8), "|",
              (a.get("time_in") or "-").ljust(5), "|",
              a.get("time_out") or "-")


# ─── Tasks ───────────────────────────────────────────────────────────────────

def add_task():
    print("\n=== ADD TASK (CHECKLIST) ===")
    user = select_cleaner()
    if user is None:
        return

    wd = get_workdays(user["username"])
    if not wd:
        print("  ! " + user["name"] + " has no workdays assigned.")
        return

    if not rooms:
        print("  ! No rooms available.")
        print("    Please add a room first (Rooms → Add room).")
        return

    room = pick(rooms, "ROOMS")
    if room is None:
        return

    day = pick(wd, "WHICH DAY? (only workdays shown)")
    if day is None:
        return

    desc = ask("What to do (e.g. Sweep the floor)", not_empty)
    if desc is None:
        return

    tasks.append({"username": user["username"],
                  "description": desc,
                  "room": room,
                  "day": day,
                  "done": False})
    print("  ✓ Task added for " + user["name"] + ":")
    print("    " + day + "  |  " + room + "  |  " + desc)


def view_tasks(username=None):
    shown = [t for t in tasks
             if username is None or t["username"] == username]
    if not shown:
        print("  No tasks yet." if username is None
              else "  No tasks assigned to you yet.")
        return shown
    print("\n  #   Status   Day        Room               Task                          iCleaner")
    print("  " + "-" * 100)
    for i in range(len(shown)):
        t = shown[i]
        u = find_user(t["username"])
        name = u["name"] if u else t["username"] + " (deleted)"
        day = t.get("day", "—")
        room = t.get("room", "—")
        print("  " + str(i + 1).ljust(3)
              + ("Done   " if t["done"] else "Pending").ljust(8)
              + day.ljust(11)
              + room.ljust(19)
              + t["description"].ljust(30)
              + name)
    return shown


def toggle_task(username=None):
    shown = view_tasks(username)
    if not shown:
        return
    i = ask("Task number",
            lambda v: None if (v.isdigit() and 1 <= int(v) <= len(shown))
                      else "Invalid number.")
    if i is None:
        return
    t = shown[int(i) - 1]
    t["done"] = not t["done"]
    u = find_user(t["username"])
    name = u["name"] if u else t["username"]
    day = t.get("day", "—")
    room = t.get("room", "—")
    print("  ✓ " + name + " → " + ("Done" if t["done"] else "Pending")
          + ": " + day + " | " + room + " | " + t["description"])

 
# ─── Menus ──────────────────────────────────────────────────────────────────

def admin_rooms_menu():
    while True:
        print("\n--- ROOMS ---")
        print(" 1 - Add room")
        print(" 2 - View all rooms")
        print(" 3 - Delete room")
        print(" 0 - Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_room()
        elif c == "2":
            view_rooms()
        elif c == "3":
            delete_room()
        elif c == "0":
            return
        else:
            print("  ! Invalid choice.")


def admin_workdays_menu():
    while True:
        print("\n--- WORKDAYS ---")
        print(" 1 - Manage a cleaner's workdays")
        print(" 2 - View all workdays (shows cleaner names)")
        print(" 0 - Back")
        c = input("Choose: ").strip()
        if c == "1":
            manage_workdays()
        elif c == "2":
            view_workdays()
        elif c == "0":
            return
        else:
            print("  ! Invalid choice.")


def admin_users_menu(admin):
    while True:
        print("\n--- USERS ---")
        print(" 1 - Create account")
        print(" 2 - View all users")
        print(" 3 - Delete user")
        print(" 0 - Back")
        c = input("Choose: ").strip()
        if c == "1":
            admin_add_user()
        elif c == "2":
            view_users()
        elif c == "3":
            delete_user(admin)
        elif c == "0":
            return
        else:
            print("  ! Invalid choice.")


def admin_schedules_menu():
    while True:
        print("\n--- SCHEDULES ---")
        print(" 1 - Add schedule (room auto-assigned)")
        print(" 2 - View all schedules (auto-assign present)")
        print(" 3 - Delete schedule")
        print(" 0 - Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_schedule()
        elif c == "2":
            view_schedules()
        elif c == "3":
            delete_schedule()
        elif c == "0":
            return
        else:
            print("  ! Invalid choice.")


def admin_attendance_menu(admin):
    while True:
        print("\n--- ATTENDANCE ---")
        print(" 1 - Mark attendance (today)")
        print(" 2 - View attendance")
        print(" 0 - Back")
        c = input("Choose: ").strip()
        if c == "1":
            mark_attendance(admin)
        elif c == "2":
            view_attendance()
        elif c == "0":
            return
        else:
            print("  ! Invalid choice.")

#dire ang ma explain sa pag run sa code hehehe hoho
def admin_tasks_menu():
    while True:
        print("\n--- TASKS (CHECKLIST) ---")
        print(" 1 - Add specific task")
        print(" 2 - View all tasks")
        print(" 3 - Mark task done/undone")
        print(" 0 - Back")
        c = input("Choose: ").strip()
        if c == "1":
            add_task()
        elif c == "2":
            view_tasks()
        elif c == "3":
            toggle_task()
        elif c == "0":
            return
        else:
            print("  ! Invalid choice.")


def admin_menu(admin):
    while True:
        print("\n=== ADMIN MENU (" + admin["name"] + ") ===")
        print(" 1 - Users")
        print(" 2 - Workdays")
        print(" 3 - Rooms")
        print(" 4 - Schedules")
        print(" 5 - Attendance")
        print(" 6 - Tasks (Checklist)")
        print(" 0 - Log out")
        c = input("Choose: ").strip()
        if c == "1":
            admin_users_menu(admin)
        elif c == "2":
            admin_workdays_menu()
        elif c == "3":
            admin_rooms_menu()
        elif c == "4":
            admin_schedules_menu()
        elif c == "5":
            admin_attendance_menu(admin)
        elif c == "6":
            admin_tasks_menu()
        elif c == "0":
            print("  Logged out.")
            return
        else:
            print("  ! Invalid choice.")


def cleaner_menu(user):
    while True:
        print("\n--- iCLEANER MENU (" + user["name"] + ") ---")
        print(" 1 - My schedule")
        print(" 2 - My tasks (Checklist)")
        print(" 3 - My attendance")
        print(" 4 - Mark a task done/undone")
        print(" 5 - My workdays")
        print(" 0 - Log out")
        c = input("Choose [0-5]: ").strip()
        if c == "1":
            view_schedules(user["username"])
        elif c == "2":
            view_tasks(user["username"])
        elif c == "3":
            my_attendance(user)
        elif c == "4":
            toggle_task(user["username"])
        elif c == "5":
            wd = get_workdays(user["username"])
            print("\n  My workdays:", ", ".join(wd) if wd else "(none assigned yet)")
        elif c == "0":
            print("  Logged out.")
            return
        else:
            print("  ! Invalid choice.")


def main():
    users.append({"name": "Admin", "username": "admin",
                  "password": "admin", "role": "admin"})

    while True:
        print("\n=== iCLEANERS SCHEDULE SYSTEM ===")
        print(" 1 - Admin login")
        print(" 2 - iCleaner login")
        print(" 0 - Exit")
        c = input("Choose: ").strip()
        if c == "1":
            a = login("admin")
            if a:
                admin_menu(a)
        elif c == "2":
            cl = login("iCleaner")
            if cl:
                cleaner_menu(cl)
        elif c == "0":
            print("Goodbye.")
            break
        else:
            print("  ! Invalid choice.")


if __name__ == "__main__":
    main()