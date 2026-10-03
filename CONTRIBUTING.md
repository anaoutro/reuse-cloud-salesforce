# Contributing

Use synthetic examples and explain changes to business rules before changing expected results.

1. Create a branch from main.
2. Run `python scripts/check_repository.py`.
3. If Apex or metadata changes, compile and run both Apex test classes in a Developer/scratch org using docs/SETUP.md.
4. Update documentation and record only checks actually executed in the pull request.

The CI workflow checks repository structure; it does not compile Apex. Platform execution is required to validate platform behavior.
