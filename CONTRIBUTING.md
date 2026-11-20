# Contributing to SDLC Master Orchestrator

Thank you for contributing! This repository is a native **Gemini Antigravity Plugin** distributed directly from GitHub.

## Skill Authoring Standards

1. **Stay Under the 24,000-Byte `SKILL.md` Body Cap**:
   - Antigravity only loads the first 24,000 bytes of a `SKILL.md` body. Put bulky reference tables, prompts, or templates inside `references/`, `resources/`, or `examples/` and link to them via relative paths (`./references/...`).
2. **Use Portable Relative Links Only**:
   - Intra-skill links: `./references/<file>.md`, `./resources/<file>.md`
   - Inter-skill links: `../<sibling-skill>/SKILL.md`
   - Never use absolute local paths (`file://<abs-path>`) or line-number anchors (`#L12-L34`) that drift across edits.
3. **Zero Proprietary or Customer References**:
   - All examples, project IDs, module names, and environment variables must be generic placeholders (`acme_mlops`, `example-cloud-project`, `APP_ENV`).
4. **Preserve Progressive Disclosure**:
   - Do not add `always_on` rules under `rules/` unless strictly required, so the plugin remains lightweight when idle.

## Local Validation Before Opening a PR

```bash
# 1. Run the cross-platform Python integrity checker
python3 scripts/validate_plugin.py

# 2. Run Antigravity's strict plugin validator (if `agy` CLI is installed)
agy plugin validate . --strict --json
```

All Pull Requests are automatically verified by `.github/workflows/validate-plugin.yml`.
