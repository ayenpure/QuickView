# Worked Example: Inspecting Aerosol Fields

This walkthrough takes you from a fresh install to a first visualization of
several aerosol quantities side by side, using only public data. It follows the
workflow behind Figure 1 of the QuickView paper (aerosol concentrations
simulated by EAMv2 on an ne30pg2 grid).

!!! warning "Work in progress"

    The procedure below uses only features described elsewhere in this
    User's Guide. Steps marked `TODO(author)` still need to be verified in the
    app and filled in (screenshots, expected values), and no numerical
    results are quoted here.

## 1. Install QuickView

Follow [Install and Launch for End Users](../setup/for_end_users.md) or
[for App Developers](../setup/for_app_developers.md).

## 2. Download the public data

| Purpose | File | Source |
| --- | --- | --- |
| Simulation output (EAMv2, ne30pg2, aerosols; 50.4 MB) | `EAMv2_ne30pg2_small_aer.nc` | [Zenodo 16922607](https://zenodo.org/records/16922607) |
| Connectivity file for the ne30pg2 grid (2.0 MB) | `connectivity_ne30pg2_TEMPEST.scrip.nc` | [Zenodo 16908566](https://zenodo.org/records/16908566) |

The two files must describe the same grid (see the
[tip on consistency](data_requirements.md)).

## 3. Load the files

1. Launch QuickView.
2. In the [toolbar](toolbar.md), set the `Connectivity File` and `Data File`
   boxes to the two files above (paste the paths or use the folder icons).
3. Click the `Load Files` button next to the `Data File` box.
4. Wait for the red circle-and-exclamation icon to turn into a green
   circle-and-check-mark icon.

## 4. Select variables

In the [control panel](control_panel.md), under the variables-at-layer-midpoints
category, search for and tick the variables used in the paper figure:

- `i_vmr_dst_a3_preAerMic`
- `i_vmr_ncl_a3_preAerMic`
- `i_vmr_so4_a1_preAerMic`
- `i_vmr_so4_a2_preAerMic`

(These names come from the saved state file used to produce the paper figure;
they should be present in `EAMv2_ne30pg2_small_aer.nc`.
`TODO(author)`: confirm in the app that all four are listed.)

Then click `LOAD VARIABLES` in the toolbar. Four contour plots appear in the
[viewport](viewport.md).

## 5. Choose the slice and projection

- Vertical level: the paper figure uses the layer-midpoint index 58.
  `TODO(author)`: state which pressure/height this corresponds to.
- Time: `TODO(author)`: which time index is shown in the paper figure.
- Map projection: Robinson (control panel, Map Projection).

## 6. Adjust the views

Per view, use the gear icon to set the colormap, a logarithmic color scale,
and a manual value range (see the [viewport](viewport.md) page). The paper
figure uses a logarithmic scale for all four views; the value ranges
and colormaps are stored in the state file
`docs/JOSS/images/state_4views_aerosol.json` on the `joss_paper` branch.
Rearrange the views by drag-and-drop.

## 7. Save and resume

Use `Save State` in the toolbar to write a JSON state file, and `Load State` to
resume later (see [the toolbar page](toolbar.md)). A state file stores the
paths of the two data files, not their contents.

## What to expect

`TODO(author)`: add a screenshot of the expected result and a short
description of what the user should see (for example, which features of the
four aerosol fields are worth noticing). No results are claimed here until
verified.
