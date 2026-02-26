# NumPy/Polars Migration Plan

Goal: Replace pandas usage on the training hot path with NumPy (and Polars only where a tabular frame is unavoidable), to reduce overhead in per‑step computations.

## What changed (Phase 1)
- env/default/rewards.py
  - RiskAdjustedReturns no longer constructs a pandas Series each step.
  - Sharpe/Sortino now accept array‑like and operate in NumPy.
  - Effect: ~15–20x speedup in a sliding‑window micro‑benchmark (window=64, 20k iters on local machine).
- env/default/observers.py
  - Removed an unused pandas import.

Benchmark script: /Users/rc/laifu/bench_tensortrade_pandas.py (same dataset and window as discussion).

## Next phases (proposed)
1) Renderers
   - Avoid unconditional DataFrame construction in BaseRenderer; move frame materialization into Plotly/Matplotlib renderers only; Screen/FileLogger stay frame‑free.
   - If Polars is available, build frames in Polars then extract numpy arrays for plotting (or convert to pandas only at the boundary if required).
2) Data acquisition/generation
   - tensortrade/data/cdd.py: switch to  and  for resampling; return NumPy/Polars depending on caller; keep pandas compatibility behind a small shim.
   - stochastic processes: remove pandas from gbm/fbm/ou/merton utilities by emitting numpy arrays and only formatting at I/O boundaries.
3) Public API surface
   - Where APIs currently promise , introduce a backend parameter (numpy|polars|pandas, default pandas) and deprecate hard pandas requirements.

## Notes
- Tests importing pandas remain untouched; these changes are backward‑compatible for callers (Sharpe/Sortino accept pandas Series as before).
- Renderers still rely on pandas today; changes will be isolated to renderer modules to avoid breaking external code.
