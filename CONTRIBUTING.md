# Contributing to QuickView

Thank you for your interest in contributing to EAM QuickView. Contributions of
all sizes are welcome: bug reports, feature requests, documentation fixes, and
code.

Note: QuickView v1.0 is this repository. Active development continues at
[Kitware/quickview](https://github.com/Kitware/quickview); for new
contributions please check that repository as well.

## Reporting bugs and requesting features

Please use the
[Issues tab on GitHub](https://github.com/ayenpure/QuickView/issues).
When reporting a bug, include:

- the QuickView version (see `quickview/__init__.py` or the releases page) and
  your operating system,
- how you installed and launched the app,
- the grid (e.g., `ne30pg2`) and model version (EAMv2, v3, EAMxx) of the data,
  and whether the file was modified by NCO/CDO or similar tools
  (see the [data format requirements](docs/userguide/data_requirements.md)),
- the full error message or terminal output, and steps to reproduce.

Feature requests should describe the scientific use case, not only the
requested change.

## Setting up a development environment

See [Install and Launch for App Developers](docs/setup/for_app_developers.md)
for the full instructions. In short:

```
git clone https://github.com/ayenpure/QuickView.git
cd QuickView
git lfs install && git lfs pull
conda env create -f quickview-env.yml
conda activate quickview
pip install -e .
```

## Running the tests

The smoke tests need no GUI and no data files:

```
pip install pytest
python -m pytest tests -v
```

These tests are also run by the GitHub workflow in
`.github/workflows/test.yml` for every push and pull request to `master` and
`release`.

## Submitting code changes

1. Open an issue (or comment on an existing one) to discuss larger changes
   before starting.
2. Fork the repository and create a topic branch from `master`.
3. Keep changes focused; one logical change per commit, with a commit message
   that describes the change.
4. Follow the existing code style. The repository uses
   [pre-commit](https://pre-commit.com/) hooks (see `.pre-commit-config.yaml`);
   run `pre-commit install` once and the hooks will check your commits.
5. Add or update tests and documentation (under `docs/`) where relevant.
6. Open a pull request against `master` describing what changed and why. Make
   sure the GitHub workflow passes.

## License

By contributing, you agree that your contributions are licensed under the
Apache License 2.0 (see [LICENSE](LICENSE)).
