# Progress Log

## Current status: Phase 3, done

## Dataset review sign-off
- Held-out SHA-256: 67720ebbe08699bb07e72733d2a6aaaae3d32482ec3e5e256c1b027b70878ef4
- Reviewed by: User (Approved in human checkpoint)
- Date: 2026-10-30
- Note: Dataset reviewed; proceeding to Phase 3.

## Phase 3: rules layer (English + Hinglish) (2026-10-30)
- Completed: Implemented agents/rules.py with regex patterns for L3 (explicit, coded, passive, method requests, Hinglish), L2 (hopelessness, withdrawal, panic), L1 (sleep, mood, stress), hyperbole context guards (preventing false crises on exam/assignment/slang contexts), and prompt injection detection.
- Files changed:
  - agents/rules.py
  - tests/test_rules.py
  - scratch/eval_rules_dev.py
  - PROGRESS.md
  - PROJECT_PLAN.md
- Commands run and REAL output (paste, do not paraphrase):
  $ pytest tests/test_rules.py -q
  .......                                                                  [100%]
  7 passed in 0.05s

  $ python scratch/eval_rules_dev.py
  === Rules-Only Dev Evaluation Summary ===
  Total dialogues: 156
  Expected Crisis (Level 3): 70
  Crisis Detected by Rules: 64
  Crisis Recall: 91.43% (64/70)
  Non-Crisis (Level 0 or 1): 62
  False Crisis Count: 0
  False Crisis Rate: 0.00% (0/62)

  Missed Crisis Cases (6):
  - PI-004 [passive_ideation]: turns=['If I got hit by a bus tomorrow, honestly it would be a huge relief.'] -> rules_scores=[0]
  - PI-006 [passive_ideation]: turns=['I just want everything to cease, to just not be here anymore.'] -> rules_scores=[0]
  - CD-005 [coded]: turns=["Soon you won't have to deal with my failures anymore."] -> rules_scores=[0]
  - CD-007 [coded]: turns=["They won't have to worry about paying my college fees anymore."] -> rules_scores=[0]
  - CD-008 [coded]: turns=['My parents will finally be happy when I am not around to trouble them.'] -> rules_scores=[0]
  - MT-007 [multi_turn]: turns=['I have been feeling hopeless for weeks.', 'I stopped going to classes completely.', "I can't cope with anything anymore."] -> rules_scores=[2, 0, 2]
- Blockers / decisions needed: None.
- Not yet verified: Phase 4.
- Next phase: Phase 4 (LLM client and classifier).

## Phase 2: synthetic dataset (before any detection code) (2026-10-30)
- Completed: Created data/README.md with labeling guide and synthetic data statement. Authored 156 dev dialogues and 44 held-out dialogues according to Section 8 specifications. Verified zero overlap between splits, correct 1-indexed peak turns for crisis, and category distributions. Created and passed tests/test_dataset.py (3 passed). Computed SHA-256 for held-out dataset and frozen.
- Files changed:
  - data/README.md
  - data/dev_dialogues.json
  - data/heldout_dialogues.json
  - tests/test_dataset.py
  - scratch/create_datasets.py
  - PROGRESS.md
  - PROJECT_PLAN.md
- Commands run and REAL output (paste, do not paraphrase):
  $ python scratch/create_datasets.py
  Wrote 156 dialogues to C:\Users\annam\OneDrive\Desktop\MannSahara\data\dev_dialogues.json
  Wrote 44 dialogues to C:\Users\annam\OneDrive\Desktop\MannSahara\data\heldout_dialogues.json
  Held-out SHA-256: 67720ebbe08699bb07e72733d2a6aaaae3d32482ec3e5e256c1b027b70878ef4

  $ pytest tests/test_dataset.py -q
  ...                                                                      [100%]
  3 passed in 0.12s
- Blockers / decisions needed: Human checkpoint: The user must review the held-out file and at least 30 random dev dialogues, confirm or adjust labels if needed, and sign off before continuing to Phase 3.
- Not yet verified: Human review of dataset.
- Next phase: Phase 3 (Rules layer: English + Hinglish).

## Phase 1: config, templates and simulated tools (2026-10-30)
- Completed: Implemented config/resources.json with Tele-MANAS (14416), KIRAN (1800-599-0019), Emergency (112), and placeholder campus cell. Implemented tools/resource_lookup.py, tools/notify_counselor_sim.py, config/templates.py with fixed crisis, referral and fallback strings, and tools/coping_tools.py with 4 evidence-based techniques. Added and passed tests/test_resources.py.
- Files changed:
  - config/resources.json
  - config/templates.py
  - tools/resource_lookup.py
  - tools/notify_counselor_sim.py
  - tools/coping_tools.py
  - tests/test_resources.py
  - PROGRESS.md
  - PROJECT_PLAN.md
- Commands run and REAL output (paste, do not paraphrase):
  $ pytest tests/test_resources.py -q
  .....                                                                    [100%]
  5 passed in 0.09s
- Blockers / decisions needed: None.
- Not yet verified: None.
- Next phase: Phase 2 (Synthetic dataset: dev + held-out).

## Phase 0: inspection and setup (2026-10-30)
- Completed: Inspected environment, Python 3.14.2, verified pre-installed packages (pydantic, pandas, streamlit, pytest, requests, python-dotenv), created directory skeleton with __init__.py files, created .gitignore, .env.example, requirements.txt, pytest.ini, tests/test_smoke.py, PROJECT_PLAN.md, initialized git repository and ran smoke test.
- Files changed:
  - .gitignore
  - .env.example
  - requirements.txt
  - pytest.ini
  - tests/test_smoke.py
  - config/__init__.py
  - agents/__init__.py
  - tools/__init__.py
  - evaluation/__init__.py
  - results/.gitkeep
  - PROJECT_PLAN.md
  - PROGRESS.md
- Commands run and REAL output (paste, do not paraphrase):
  $ pytest -q
  .                                                                        [100%]
  1 passed in 4.56s
- Blockers / decisions needed: None for Phase 0.
- Not yet verified: None.
- Next phase: Phase 1 (Config, templates and simulated tools).

## Dataset review sign-off
- Held-out SHA-256: 67720ebbe08699bb07e72733d2a6aaaae3d32482ec3e5e256c1b027b70878ef4 Reviewed by: User (Approved) Date: 2026-10-30

