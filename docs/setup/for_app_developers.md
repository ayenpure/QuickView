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

## Requirements

- [conda](https://docs.conda.io/) (Miniconda or Miniforge) with access to the
  `conda-forge` channel
- Git and [Git LFS](https://git-lfs.com/) (the bundled globe/connectivity
  files and documentation images are stored with LFS):
  run `git lfs install && git lfs pull` after cloning
- Free disk space: about 2 GB for the conda environment (see below)

!!! info "Disk space and memory"

    - **Disk:** the conda environment created from `quickview-env.yml`
      (Python 3.13 + ParaView 5.13.3 + their dependencies) occupied about
      1.5 GB, and about 1.6 GB after `pip install .`
      (measured on macOS arm64; conda package cache is additional).
      The optional [sample data](https://zenodo.org/records/16922607) is
      369 MB in total, and the [connectivity files](https://zenodo.org/records/16908566)
      range from 49 kB (ne4pg2) to 2.3 GB (ne1024pg2).
      Building the Tauri/PyInstaller application needs additional space
      that has not been measured. <!-- TODO(author): measure -->
    - **Memory:** <!-- TODO(author): recommended RAM per grid size
      (e.g., ne4 / ne30 / ne120 / ne256) has not been measured. -->
      Recommended memory has not been determined yet; it depends on the
      grid resolution, number of variables loaded, and number of time steps.

---

## Install ParaView and QuickView

QuickView uses the ParaView Python modules (`paraview`, `vtk`) at run time.
The standard way to get them is from
[conda-forge](https://conda-forge.org/); the provided environment file pins
ParaView 5.13.3 and Python 3.13, so no separate ParaView download is needed.

```
# Set up conda environment (installs python=3.13 and paraview=5.13.3)
conda env create -f quickview-env.yml
conda activate quickview

# Install QuickView
pip install -e .
```

To verify the installation:

```
python -c "import paraview; print(paraview.__version__)"
python -m quickview.app --help
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
