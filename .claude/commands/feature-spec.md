Read `specs/roadmap.md` to identify the next pending phase (status ⏳ or unmarked).
Also read `specs/mission.md` and `specs/tech-stack.md` for project context.

Then use the AskUserQuestion tool to ask all three of the following questions in a single grouped call — do NOT write any files before receiving answers:

1. **Feature name and description** — What should the directory be called (will become `YYYY-MM-DD-<name>`) and what is a one-sentence description of what this phase delivers?
2. **Key decisions and constraints** — What design choices, dependencies, scope limits, or context should be captured in `requirements.md`? (e.g. model choices, data format, API constraints, what is explicitly out of scope)
3. **Validation criteria** — How will you know this feature is complete and ready to merge? List the checks that must pass (tests, output files, metric thresholds, manual checks, etc.)

Once you have the answers:

1. Create a git branch named `feature/<name>` (use the feature name from answer 1, lowercased, hyphens for spaces).
2. Create the directory `specs/YYYY-MM-DD-<name>/` using today's date.
3. Write three files into that directory:

**plan.md** — A numbered list of task groups. Each group has a heading and 3–6 concrete, actionable subtasks. Derive the groups from the roadmap phase description and the user's answers. Format:
```
# Plan: <Feature Name>

## 1. <Group name>
- [ ] task
- [ ] task

## 2. <Group name>
...
```

**requirements.md** — Scope, decisions, and context. Sections: Overview, In Scope, Out of Scope, Key Decisions, Dependencies, Open Questions. Populate from the roadmap, mission.md, tech-stack.md, and the user's answers.

**validation.md** — How to confirm the implementation is correct and ready to merge. Sections: Automated Checks, Output Artifacts, Manual Checks, Merge Criteria. Populate from the user's validation answer and the project's testing conventions in tech-stack.md.

After writing the files, print a short summary: branch name, directory created, and a one-line description of each file.
