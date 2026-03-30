from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CareTask:
    task_type: str
    duration_minutes: int
    priority: Priority
    scheduled_date: date
    frequency: str = "once"  # "once", "daily", or "weekly"
    is_completed: bool = False

    def mark_complete(self) -> "CareTask | None":
        """Mark this task complete and return the next occurrence if recurring, else None."""
        self.is_completed = True
        if self.frequency == "daily":
            return CareTask(self.task_type, self.duration_minutes, self.priority,
                            self.scheduled_date + timedelta(days=1), self.frequency)
        if self.frequency == "weekly":
            return CareTask(self.task_type, self.duration_minutes, self.priority,
                            self.scheduled_date + timedelta(weeks=1), self.frequency)
        return None

    def is_due_today(self) -> bool:
        """Return True if this task is scheduled for today."""
        return self.scheduled_date == date.today()


@dataclass
class Pet:
    name: str
    species: str
    age: int
    weight: float
    tasks: List[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def complete_task(self, task: CareTask) -> None:
        """Mark a task complete and append the next occurrence to this pet's task list if the task recurs."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)

    def get_pending_tasks(self) -> List[CareTask]:
        """Return all tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.is_completed]

    def get_summary(self) -> str:
        """Return a readable summary of the pet and their pending task count."""
        pending = len(self.get_pending_tasks())
        return f"{self.name} ({self.species}, age {self.age}, {self.weight}kg) — {pending} pending task(s)"


class Owner:
    def __init__(self, name: str, available_time_minutes: int, preferences: str = ""):
        self.name = name
        self.available_time_minutes = available_time_minutes
        self.preferences = preferences
        self._pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self._pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return a copy of the owner's pet list."""
        return list(self._pets)

    def get_all_tasks(self) -> List[CareTask]:
        """Return a flat list of all tasks across every pet the owner has."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.tasks)
        return tasks


class DailyPlanner:
    def __init__(self, owner: Owner, plan_date: date = None):
        self.owner = owner
        self.date = plan_date or date.today()

    def generate_plan(self) -> List[CareTask]:
        """Return today's prioritized task list fitted within the owner's time budget."""
        due_today = [
            t for t in self.owner.get_all_tasks()
            if t.is_due_today() and not t.is_completed
        ]

        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_tasks = sorted(due_today, key=lambda t: priority_order[t.priority])

        plan = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_time_minutes:
                plan.append(task)
                time_used += task.duration_minutes

        return plan

    def explain_plan(self) -> str:
        """Return a human-readable string describing today's scheduled tasks and time used."""
        plan = self.generate_plan()
        if not plan:
            return f"No tasks scheduled for {self.date}."

        lines = [f"Plan for {self.date} ({self.owner.available_time_minutes} min available):"]
        time_used = 0
        for task in plan:
            lines.append(
                f"  - [{task.priority.value.upper()}] {task.task_type} — {task.duration_minutes} min"
            )
            time_used += task.duration_minutes
        lines.append(f"Total: {time_used} / {self.owner.available_time_minutes} min used")
        return "\n".join(lines)

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> List[CareTask]:
        """Return tasks filtered by completion status and/or pet name."""
        results = []
        for pet in self.owner.get_pets():
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.is_completed != completed:
                    continue
                results.append(task)
        return results

    def sort_by_time(self) -> List[CareTask]:
        """Return all of today's pending tasks sorted by duration, shortest first."""
        due_today = [
            t for t in self.owner.get_all_tasks()
            if t.is_due_today() and not t.is_completed
        ]
        return sorted(due_today, key=lambda t: t.duration_minutes)

    def detect_conflicts(self) -> List[str]:
        """Return a list of warning strings for scheduling conflicts; empty list means no conflicts."""
        warnings = []

        # Check for duplicate task types on the same day per pet
        for pet in self.owner.get_pets():
            seen = {}
            for task in pet.tasks:
                if task.is_due_today() and not task.is_completed:
                    if task.task_type in seen:
                        warnings.append(
                            f"WARNING: '{task.task_type}' is scheduled more than once today for {pet.name}."
                        )
                    seen[task.task_type] = True

        # Check for tasks that exceed the time budget
        due_today = [
            t for t in self.owner.get_all_tasks()
            if t.is_due_today() and not t.is_completed
        ]
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_tasks = sorted(due_today, key=lambda t: priority_order[t.priority])

        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes > self.owner.available_time_minutes:
                warnings.append(
                    f"WARNING: '{task.task_type}' ({task.duration_minutes} min) doesn't fit "
                    f"— only {self.owner.available_time_minutes - time_used} min remaining."
                )
            else:
                time_used += task.duration_minutes

        return warnings

    def get_completed_tasks(self) -> List[CareTask]:
        """Return all tasks across the owner's pets that have been marked complete."""
        return [t for t in self.owner.get_all_tasks() if t.is_completed]