# CLAUDE.md

## Modules
Top-level modules in this repo: `test-agent`, `test-agent-v2`, `pomodoro`.

## Commit conventions
When committing changes to a module:

1. **Prefix the commit title** with `[<module>]`, e.g. `[test-agent-v2] Log per-call token usage`.
   If a commit spans multiple modules, list them: `[test-agent,test-agent-v2]`.
2. **Update that module's `README.md` in the same commit:**
   - Add a `## Changelog` bullet summarizing the change.
   - Refresh the list of files under `## Files` if files were added or removed.
3. **Stage the README** so it lands in the same commit as the code change.
