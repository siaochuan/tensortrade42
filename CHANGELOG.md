# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Fix: Environment `step()` compatibility with `gymnasium` and older `gym` APIs — `step()` now returns a 4-tuple `(obs, reward, done, info)` where `done = terminated or truncated` to retain backwards compatibility. (See `tensortrade/env/generic/environment.py`)
- Fix: Tests standardized to `setup_method` to ensure `pytest` consistently discovers per-test setup. (See `tests/tensortrade/unit/env/default/test_rewards.py`)

---

(These changes were applied to make the project runnable in environments using `gymnasium` and modern `pytest`. All unit tests pass locally: `218 passed, 2 skipped`.)