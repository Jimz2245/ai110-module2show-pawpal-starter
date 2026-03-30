PawPal+ Project Reflection
1. System Design
a. Initial design

Briefly describe your initial UML design.
What classes did you include, and what responsibilities did you assign to each?

The first version of my design featured four primary classes: Pet, CareTask, Owner, and DailyPlanner.

Pet captures core details about each animal, including name, species, age, and weight, with the ability to generate a readable description.
CareTask defines individual care activities like walks or medication, storing information about the activity type, how long it takes, its importance level, and whether it's been done. It can mark completion and determine if it needs to happen today.
Owner contains the user's information, available time per day, and personal preferences. It maintains a collection of pets and handles adding new ones and looking them up.
DailyPlanner serves as the main scheduling engine. It works with an owner and their tasks to build a prioritized schedule, provide rationale for the ordering, and track task completion.

b. Design changes

Did your design change during implementation?
If yes, describe at least one change and why you made it.

The design evolved significantly during implementation. The biggest modification was to CareTask: initially, it lacked any connection to a particular Pet and had no timing information, which meant the planner couldn't determine task ownership or scheduling relevance. I added pet: Pet to establish the relationship and scheduled_date: date to enable the is_due_today() method to function properly.
Another important change involved replacing the priority string field with a Priority enumeration. String-based priorities created opportunities for silent errors from case mismatches that would corrupt sorting behavior. The enum approach ensures invalid values fail immediately during creation instead of causing subtle issues later.

2. Scheduling Logic and Tradeoffs
a. Constraints and priorities

What constraints does your scheduler consider (for example: time, priority, preferences)?
How did you decide which constraints mattered most?

My scheduler works with two primary constraints: the owner's daily time availability and task importance levels (high, medium, low). Tasks get sorted by importance, then added sequentially to the schedule while time permits. The system identifies issues like repeated tasks and time overruns through conflict checking.
I prioritized importance first because critical needs like medication or feeding cannot be safely skipped, unlike activities such as enrichment. Time availability ranked second since daily hours are inherently limited, requiring difficult choices. Owner preferences were built into the data model but aren't yet used in sorting decisions—they're noted as a planned enhancement.
b. Tradeoffs

Describe one tradeoff your scheduler makes.
Why is that tradeoff reasonable for this scenario?

The scheduler employs a greedy selection approach: after sorting by importance, it includes each task that fits within available time, immediately stopping when a task won't fit rather than checking if smaller tasks could still be accommodated. While a more sophisticated algorithm like knapsack optimization could improve time utilization, it would add substantial complexity. For pet care scheduling—where clarity and predictability outweigh marginal efficiency gains—the simpler method is justified.
During code review, AI recommended condensing the accumulation loop in generate_plan() using itertools.accumulate. Though more compact, this version sacrificed readability. I retained the explicit loop because it clearly communicates the logic and remains easier to modify as requirements evolve.

3. AI Collaboration
a. How you used AI

How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
What kinds of prompts or questions were most helpful?

AI tools supported my work primarily through architectural planning and code improvement. When starting the design, I sought input on class organization and responsibility distribution, which clarified essential components and their interactions. A representative prompt was: "How would you design a pet care scheduling system in Python? What classes and methods would you include?"
b. Judgment and verification

Describe one moment where you did not accept an AI suggestion as-is.
How did you evaluate or verify what the AI suggested?

A key instance occurred when AI proposed using itertools.accumulate to streamline the scheduling loop. While more compact, the suggestion reduced code clarity significantly. I weighed compactness against comprehensibility, ultimately recognizing that since this logic is central to the system and likely to need updates, readability and ease of modification outweighed brevity. The explicit loop structure remained in place.

4. Testing and Verification
a. What you tested

What behaviors did you test?
Why were these tests important?

I validated several critical system behaviors:

Sorting: Confirmed tasks appear in duration order and that completed or future tasks don't appear in today's schedule.
Recurrence: Verified that completing daily tasks creates tomorrow's entry, weekly tasks schedule seven days ahead, and once tasks don't repeat.
Conflict detection: Ensured duplicate task types on one day trigger warnings, time budget violations generate alerts, and conflict-free schedules produce no warnings.
Edge cases: Tested that pets without tasks return empty lists with proper summaries, and owners without pets produce empty plans without crashing.

These tests were essential because they validate the system's core functionality—proper task prioritization, accurate recurrence handling, and proactive issue identification—all of which are critical for reliable pet care management.
b. Confidence

How confident are you that your scheduler works correctly?
What edge cases would you test next if you had more time?

I have strong confidence in the core functionality, supported by all 12 tests passing. The test suite addresses priority ordering, time constraints, task recurrence, and conflict identification—the system's fundamental capabilities.
With additional time, I would explore:

Input validation for problematic values like negative durations or empty task type strings.
Tasks scheduled in the past or distant future to confirm proper exclusion from today's schedule.
Scenarios with multiple pets having overlapping tasks to verify correct aggregation and cross-pet sorting.


5. Reflection
a. What went well

What part of this project are you most satisfied with?

I'm most pleased with the design and execution of the scheduling logic within DailyPlanner. The system effectively ranks tasks by importance and allocates them within time constraints while clearly explaining scheduling decisions. The conflict detection feature stands out as particularly valuable, proactively flagging duplicate tasks and time budget issues to help owners manage pet care more effectively.
b. What you would improve

If you had another iteration, what would you improve or redesign?

In a future iteration, I would integrate owner preferences into the scheduling algorithm. Currently, these preferences are stored but not actively used in task prioritization. I would enhance generate_plan() to respect owner-specified task categories like "essential" or "optional" based on individual circumstances and priorities. Additionally, I would implement input validation at system entry points to prevent invalid data from propagating through the system.
c. Key takeaway

What is one important thing you learned about designing systems or working with AI on this project?

The most significant lesson is that AI suggestions require careful human evaluation rather than automatic acceptance. Not every AI-generated recommendation suits the project's specific context, and it's essential to weigh factors like code clarity, long-term maintainability, and user needs when deciding whether to implement AI proposals. This project highlighted the value of combining AI assistance with thoughtful judgment to build systems that are both functional and sustainable.
