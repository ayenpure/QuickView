# Install and Launch for App Developers

At version 1.0, QuickView is expected to be installed and used from a personal
computer with the data files also being local. Future versions will support the
server-client model allowing access to remote data.

Releases so far have focused on macOS. Support for more systems will be added in
the near [future](../future.md).

---

## Clone the repo

```
git clone https://github.com/ayenpure/QuickView.git
cd QuickView
```

---

## Install basic requirements

```
# Set up conda environment
conda env create -f quickview-env.yml
conda activate quickview

# Install QuickView
pip install -e .
```

---

## Launch the app from command line

To launch the EAM QuickView GUI in its dedicated window, use

```
python -m quickview.app --data /path/to/your/data.nc --conn /path/to/connectivity.nc
```

To launch server only (no browser popup), use

```
python --server -m quickview.app --data /path/to/your/data.nc --conn /path/to/connectivity.nc
```

---

## Development utilities

Configure and build a local tauri app for QuickView

```
./scripts/setup_tauri.sh && cargo tauri build
```

or, build for debug mode

```
./scripts/setup_tauri.sh && cargo tauri build --debug
```

The above commands will install quickview in the current environment, run
pyInstaller, and package the Tauri app

Initiate release process -- this creates a PR for release on github

```
./scripts/release.sh patch/minor/major
```

This script after will bump the version based on the release type requested
(patch/minor/major). It creates a tag from the master with the bumped version
number and will create a PR with necessary information. The PR when merged to
the release branch trigges the automated Tauri build step on GitHub.
