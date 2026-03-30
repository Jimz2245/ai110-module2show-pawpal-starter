from datetime import date, timedelta
from pawpal_system import CareTask, DailyPlanner, Owner, Pet, Priority


def test_mark_complete():
    task = CareTask("Walk", 30, Priority.HIGH, date.today())
    task.mark_complete()
    assert task.is_completed is True


def test_pet_add_task():
    pet = Pet("Buddy", "Dog", 3, 12.5)
    task = CareTask("Walk", 30, Priority.HIGH, date.today())
    pet.add_task(task)
    assert len(pet.tasks) == 1


# --- Sorting Correctness ---

def test_sort_by_time_returns_shortest_first():
    """Tasks due today should be returned in ascending duration order."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "Dog", 3, 12.5)
    owner.add_pet(pet)
    pet.add_task(CareTask("Bath", 60, Priority.LOW, date.today()))
    pet.add_task(CareTask("Walk", 30, Priority.HIGH, date.today()))
    pet.add_task(CareTask("Feed", 10, Priority.MEDIUM, date.today()))

    planner = DailyPlanner(owner)
    sorted_tasks = planner.sort_by_time()

    durations = [t.duration_minutes for t in sorted_tasks]
    assert durations == sorted(durations), "Tasks should be sorted shortest-first"


def test_sort_by_time_excludes_completed_and_future_tasks():
    """Completed tasks and tasks not due today must not appear in sort_by_time."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "Dog", 3, 12.5)
    owner.add_pet(pet)

    today_task = CareTask("Walk", 30, Priority.HIGH, date.today())
    future_task = CareTask("Bath", 60, Priority.LOW, date.today() + timedelta(days=1))
    done_task = CareTask("Feed", 10, Priority.MEDIUM, date.today())
    done_task.is_completed = True

    pet.add_task(today_task)
    pet.add_task(future_task)
    pet.add_task(done_task)

    planner = DailyPlanner(owner)
    result = planner.sort_by_time()

    assert result == [today_task]


# --- Recurrence Logic ---

def test_daily_task_creates_next_day_on_complete():
    """Completing a daily task should append a new task scheduled for tomorrow."""
    pet = Pet("Luna", "Cat", 2, 4.0)
    task = CareTask("Feed", 10, Priority.HIGH, date.today(), frequency="daily")
    pet.add_task(task)
    pet.complete_task(task)

    assert task.is_completed is True
    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.scheduled_date == date.today() + timedelta(days=1)
    assert next_task.frequency == "daily"
    assert not next_task.is_completed


def test_weekly_task_creates_next_week_on_complete():
    """Completing a weekly task should append a new task scheduled 7 days later."""
    pet = Pet("Luna", "Cat", 2, 4.0)
    task = CareTask("Groom", 20, Priority.MEDIUM, date.today(), frequency="weekly")
    pet.add_task(task)
    pet.complete_task(task)

    next_task = pet.tasks[1]
    assert next_task.scheduled_date == date.today() + timedelta(weeks=1)


def test_once_task_does_not_recur():
    """Completing a one-time task should not add any new tasks."""
    pet = Pet("Buddy", "Dog", 3, 12.5)
    task = CareTask("Vet", 45, Priority.HIGH, date.today(), frequency="once")
    pet.add_task(task)
    pet.complete_task(task)

    assert len(pet.tasks) == 1


# --- Conflict Detection ---

def test_conflict_detected_for_duplicate_task_type_same_pet():
    """Two tasks of the same type scheduled today for the same pet should trigger a warning."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "Dog", 3, 12.5)
    owner.add_pet(pet)
    pet.add_task(CareTask("Walk", 30, Priority.HIGH, date.today()))
    pet.add_task(CareTask("Walk", 30, Priority.HIGH, date.today()))

    planner = DailyPlanner(owner)
    warnings = planner.detect_conflicts()

    assert any("Walk" in w and "Buddy" in w for w in warnings)


def test_conflict_detected_when_tasks_exceed_time_budget():
    """Tasks whose total duration exceeds available time should trigger a budget warning."""
    owner = Owner("Alice", 40)  # only 40 min available
    pet = Pet("Buddy", "Dog", 3, 12.5)
    owner.add_pet(pet)
    pet.add_task(CareTask("Walk", 30, Priority.HIGH, date.today()))
    pet.add_task(CareTask("Bath", 30, Priority.MEDIUM, date.today()))

    planner = DailyPlanner(owner)
    warnings = planner.detect_conflicts()

    assert any("Bath" in w for w in warnings)


def test_no_conflicts_when_schedule_is_clean():
    """A well-formed schedule with no duplicates and sufficient time should return no warnings."""
    owner = Owner("Alice", 120)
    pet = Pet("Buddy", "Dog", 3, 12.5)
    owner.add_pet(pet)
    pet.add_task(CareTask("Walk", 30, Priority.HIGH, date.today()))
    pet.add_task(CareTask("Feed", 10, Priority.MEDIUM, date.today()))

    planner = DailyPlanner(owner)
    assert planner.detect_conflicts() == []


# --- Edge Cases ---

def test_pet_with_no_tasks_returns_empty_pending():
    """A pet with no tasks should report zero pending tasks without errors."""
    pet = Pet("Ghost", "Cat", 1, 3.2)
    assert pet.get_pending_tasks() == []
    assert "0 pending task(s)" in pet.get_summary()


def test_owner_with_no_pets_generates_empty_plan():
    """An owner with no pets should produce an empty plan without errors."""
    owner = Owner("Bob", 60)
    planner = DailyPlanner(owner)
    assert planner.generate_plan() == []