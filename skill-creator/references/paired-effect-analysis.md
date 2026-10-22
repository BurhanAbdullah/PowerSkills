# Paired benchmark effect analysis

This standalone command adds inferential statistics to the descriptive summaries emitted by aggregate_benchmark.py. It compares two configurations only on matching (eval_id, run_number) observations and reports mean, median, sample standard deviation, a percentile-bootstrap 95% confidence interval, a Monte-Carlo sign-flip p-value, and the matched identifiers. Positive values mean configuration A is higher than configuration B. Treat small samples as exploratory; the result is not proof of causality.

Run from the repository root:

    python skill-creator/scripts/paired_effect_analysis.py path/to/benchmark.json --config-a with_skill --config-b without_skill --metric pass_rate --bootstrap-samples 10000 --seed 2026 --output path/to/paired_effect.json

Focused regression tests:

    python -m pytest skill-creator/tests/test_paired_effect_analysis.py -q

The script uses only the Python standard library.
