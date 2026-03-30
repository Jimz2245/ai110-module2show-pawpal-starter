import streamlit as st
from datetime import date
from pawpal_system import CareTask, Pet, Owner, DailyPlanner, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_time_minutes=60)

owner: Owner = st.session_state.owner

# --- Owner setup ---
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Your name", value=owner.name or "Jordan")
with col2:
    owner.available_time_minutes = st.number_input(
        "Available time today (minutes)", min_value=10, max_value=480, value=owner.available_time_minutes
    )

st.divider()

# --- Add a pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species, age=pet_age, weight=0.0)
    owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}!")

pets = owner.get_pets()
if pets:
    st.write("**Your pets:**", ", ".join(p.get_summary() for p in pets))

st.divider()

# --- Add a task ---
st.subheader("Add a Task")

if not pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    pet_names = [p.name for p in pets]
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        target_pet = st.selectbox("Assign to pet", pet_names)
    with col2:
        task_title = st.text_input("Task", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority_str = st.selectbox("Priority", ["high", "medium", "low"])
    with col5:
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])

    if st.button("Add task"):
        selected_pet = next(p for p in pets if p.name == target_pet)
        priority_map = {"high": Priority.HIGH, "medium": Priority.MEDIUM, "low": Priority.LOW}
        new_task = CareTask(
            task_type=task_title,
            duration_minutes=int(duration),
            priority=priority_map[priority_str],
            scheduled_date=date.today(),
            frequency=frequency,
        )
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {target_pet}.")

    if any(p.tasks for p in pets):
        st.write("**Current tasks (all):**")
        rows = []
        for p in pets:
            for t in p.tasks:
                rows.append({
                    "Pet": p.name,
                    "Task": t.task_type,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.value,
                    "Repeats": t.frequency,
                    "Done": "✅" if t.is_completed else "⬜",
                })
        st.table(rows)

st.divider()

# --- Generate schedule ---
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    if not pets:
        st.warning("Add at least one pet and task first.")
    else:
        planner = DailyPlanner(owner)

        # --- Conflict warnings (shown first so owner can act) ---
        conflicts = planner.detect_conflicts()
        if conflicts:
            st.error("**Scheduling conflicts detected — review before starting your day:**")
            for msg in conflicts:
                # Strip the "WARNING: " prefix since the UI provides context
                clean = msg.replace("WARNING: ", "")
                st.warning(f"⚠️ {clean}")

        # --- Priority-sorted plan ---
        plan = planner.generate_plan()
        if not plan:
            st.info("No tasks fit today's schedule. Try adding tasks or increasing your available time.")
        else:
            priority_badge = {
                "high": "🔴 HIGH",
                "medium": "🟡 MEDIUM",
                "low": "🟢 LOW",
            }
            time_used = sum(t.duration_minutes for t in plan)

            st.success(
                f"Plan ready — **{time_used} of {owner.available_time_minutes} min** scheduled "
                f"across {len(plan)} task(s)."
            )

            plan_rows = [
                {
                    "Priority": priority_badge.get(t.priority.value, t.priority.value),
                    "Task": t.task_type,
                    "Duration (min)": t.duration_minutes,
                    "Repeats": t.frequency,
                }
                for t in plan
            ]
            st.table(plan_rows)

        st.divider()

        # --- Sorted by duration (quick-wins view) ---
        st.subheader("Tasks by Duration (shortest first)")
        sorted_tasks = planner.sort_by_time()
        if sorted_tasks:
            sorted_rows = [
                {
                    "Task": t.task_type,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.value,
                    "Repeats": t.frequency,
                }
                for t in sorted_tasks
            ]
            st.table(sorted_rows)
        else:
            st.info("No pending tasks due today.")