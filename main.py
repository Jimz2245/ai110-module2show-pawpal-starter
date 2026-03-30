from datetime import date
from pawpal_system import CareTask, Pet, Owner, DailyPlanner, Priority

# Create owner
owner = Owner(name="Daniel", available_time_minutes=90)

# Create pets
buddy = Pet(name="Buddy", species="Dog", age=3, weight=12.5)
luna = Pet(name="Luna", species="Cat", age=5, weight=4.2)

# Add tasks — mix of once/daily/weekly, out of order
buddy.add_task(CareTask("Morning Walk", 30, Priority.HIGH, date.today(), frequency="daily"))
buddy.add_task(CareTask("Feeding", 10, Priority.HIGH, date.today(), frequency="daily"))
buddy.add_task(CareTask("Bath Time", 25, Priority.LOW, date.today(), frequency="weekly"))

luna.add_task(CareTask("Playtime / Enrichment", 15, Priority.LOW, date.today(), frequency="daily"))
luna.add_task(CareTask("Grooming", 20, Priority.MEDIUM, date.today(), frequency="weekly"))
luna.add_task(CareTask("Meds", 5, Priority.HIGH, date.today(), frequency="once"))

# Add a duplicate task to trigger a same-day conflict warning
buddy.add_task(CareTask("Morning Walk", 30, Priority.HIGH, date.today(), frequency="once"))

# Add a task that overflows the time budget
buddy.add_task(CareTask("Vet Visit", 60, Priority.LOW, date.today(), frequency="once"))

# Complete a daily task — should auto-schedule tomorrow
buddy.complete_task(buddy.tasks[1])  # Feeding (daily)

# Register pets with owner
owner.add_pet(buddy)
owner.add_pet(luna)

planner = DailyPlanner(owner)

# --- Original plan ---
# --- Conflict detection ---
print("=== Conflict Detection ===")
conflicts = planner.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(w)
else:
    print("No conflicts detected.")

print()
print("=== PawPal+ ===")
for pet in owner.get_pets():
    print(pet.get_summary())
print()
print(planner.explain_plan())

# --- Sorted by duration ---
print("\n=== Sorted by Time (shortest first) ===")
for t in planner.sort_by_time():
    print(f"  {t.task_type} — {t.duration_minutes} min")

# --- Filter: pending tasks only ---
print("\n=== Pending Tasks (all pets) ===")
for t in planner.filter_tasks(completed=False):
    print(f"  {t.task_type} — done: {t.is_completed}")

# --- Filter: completed tasks only ---
print("\n=== Completed Tasks ===")
for t in planner.filter_tasks(completed=True):
    print(f"  {t.task_type} — done: {t.is_completed}")

# --- Show auto-scheduled next occurrences ---
print("\n=== All of Buddy's Tasks (incl. auto-scheduled) ===")
for t in buddy.tasks:
    print(f"  {t.task_type} | {t.scheduled_date} | freq={t.frequency} | done={t.is_completed}")

# --- Filter: Buddy's tasks only ---
print("\n=== Buddy's Tasks ===")
for t in planner.filter_tasks(pet_name="Buddy"):
    print(f"  {t.task_type} — {t.priority.value}")

# --- Filter: Luna's pending tasks ---
print("\n=== Luna's Pending Tasks ===")
for t in planner.filter_tasks(completed=False, pet_name="Luna"):
    print(f"  {t.task_type} — {t.priority.value}")