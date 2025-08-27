---
title:
  "QuickView: An Interactive Visualization Tool for Atmospheric Model Analysis"
tags:
  - Python
  - atmospheric science
  - climate modeling
  - visualization
  - E3SM
  - ParaView
  - interactive analysis
authors:
  - name: Abhishek Yenpure
    orcid: 0000-0000-0000-0000
    affiliation: 1
    corresponding: true
  - name: Berk Geveci
    orcid: 0000-0000-0000-0000
    affiliation: 1
  - name: Sebastien Jourdain
    orcid: 0000-0000-0000-0000
    affiliation: 1
  - name: Hui Wan
    orcid: 0000-0000-0000-0000
    affiliation: 2
  - name: Kai Zhang
    orcid: 0000-0000-0000-0000
    affiliation: 2
affiliations:
  - name: Kitware, Inc., United States
    index: 1
  - name: Pacific Northwest National Laboratory, United States
    index: 2
date: 27 August 2025
bibliography: paper.bib
---

# Summary

QuickView is an open-source, interactive visualization tool designed
specifically for scientists working with the Energy Exascale Earth System Model
(E3SM) Atmosphere Model (EAM). The tool provides an intuitive, web-based
graphical user interface that leverages ParaView's powerful visualization
capabilities without requiring users to navigate ParaView's complex interface.
QuickView addresses a critical need in atmospheric sciences by offering
specialized support for EAM data formats, globe and map projections, and
multi-variable visualization workflows commonly used in climate model analysis.

The tool is built using Python and the Trame framework, packaged as a
cross-platform desktop application using Tauri. This architecture enables rapid
iteration and deployment while maintaining the performance benefits of
ParaView's underlying visualization engine. QuickView supports EAM versions 2,
3, and the evolving version 4 (EAMxx), making it accessible to the broad E3SM
user community.

# Statement of need

Climate scientists working with atmospheric model output face significant
challenges in data exploration and analysis. While comprehensive visualization
tools like ParaView and VisIt are powerful, they present steep learning curves
for domain scientists who are not visualization experts [@Ahrens2005;
@Childs2012]. These general-purpose tools often lack out-of-the-box support for
atmospheric science requirements such as:

- Native handling of unstructured cubed-sphere grids used by EAM
- Specialized map projections common in atmospheric sciences
- Domain-specific data structures and variable categorizations
- Streamlined workflows for multi-variable comparative analysis

Traditional tools in atmospheric sciences, such as ncview [@Pierce2019] and
ncvis, provide basic data inspection capabilities but are limited in their
ability to handle modern, high-resolution climate datasets or support
sophisticated visualization workflows. QuickView fills this gap by providing a
domain-specific interface that reduces the time from data to scientific insight.

The primary goal of QuickView is to enable rapid "first glance" analysis of
simulation output, allowing scientists to quickly inspect characteristic values
of physical quantities, examine their variations across geographical location,
altitude, and time, and perform comparative analysis across different variables.
This capability is essential for model development, validation, and scientific
discovery in atmospheric sciences.

# Features and Functionality

## Core Visualization Capabilities

QuickView provides specialized support for EAM's cubed-sphere grid structure
through custom ParaView plugins that handle the complex connectivity information
required for proper visualization. The tool automatically categorizes variables
based on their dimensionality:

- **2D variables** (time × ncol): Surface quantities varying with latitude and
  longitude
- **3D variables** (time × ncol × lev/ilev): Atmospheric fields with vertical
  structure at layer midpoints or interfaces

Variables are displayed using appropriate coordinate transformations, with
support for multiple map projections including orthographic, cylindrical
equidistant, and Mollweide projections.

## Multi-variable Analysis

A key strength of QuickView is its support for simultaneous visualization of
multiple variables through a drag-and-drop interface. Users can create custom
layouts with up to multiple viewports, each displaying different variables or
different vertical levels of the same variable. This capability enables rapid
comparative analysis essential for understanding complex atmospheric processes.

## Data Format Support

QuickView is designed to work with EAM history output files in NetCDF format,
supporting the pg2 (physics grid) data structure used by EAM versions 2, 3, and
the intermediate version toward EAMv4. The tool handles:

- Native EAM output files
- Post-processed files created with NCO, CDO, or custom scripts
- Time-averaged and variable-subset files
- Missing value handling through `missing_value` and `_FillValue` attributes

## Session Persistence

QuickView includes comprehensive session management, allowing users to save and
restore complete visualization states including:

- Active variables and their display properties
- Camera positions and orientations
- Color mapping configurations
- Multi-view layouts
- Data file associations

This feature supports iterative analysis workflows and enables collaboration by
sharing visualization configurations.

# Software Architecture

## Multi-layer Design

QuickView employs a multi-layer architecture that separates concerns between
data processing, visualization, and user interface:

1. **Data Layer**: Custom ParaView plugins handle EAM-specific data reading and
   geometric transformations
2. **Processing Layer**: ParaView pipeline management coordinates data flow and
   applies filters
3. **Interface Layer**: Trame framework provides the web-based user interface
   with real-time state synchronization
4. **Application Layer**: Tauri wrapper creates the native desktop experience
   across platforms

## Custom ParaView Plugins

The core visualization capabilities are implemented through specialized ParaView
plugins:

- **EAM Reader**: Handles NetCDF data loading with proper variable
  categorization
- **EAM Projection Filter**: Implements atmospheric science-specific map
  projections
- **EAM Grid Lines**: Provides geographic reference overlays
- **EAM Filters**: Implements domain-specific data processing operations

## Web-based Interface

The user interface is built using Trame, which enables seamless integration
between ParaView's Python interface and modern web technologies. The interface
components include:

- **Variable Selection**: Hierarchical display of available 2D and 3D variables
- **Projection Selection**: Interactive selection of map projections and
  parameters
- **Slice Selection**: Vertical level selection for 3D variables
- **View Settings**: Color mapping and rendering parameter controls
- **Toolbar**: File operations, state management, and view controls

## Cross-platform Deployment

Tauri provides the desktop application wrapper, handling:

- Native file system access for data loading
- Cross-platform distribution (macOS, Windows, Linux)
- Automatic dependency management through PyInstaller
- Sidecar pattern for running the Python visualization server

# Impact and Usage

QuickView has been adopted by researchers and developers working with E3SM
atmospheric simulations. The tool significantly reduces the time required for
initial data exploration, enabling scientists to quickly identify interesting
features in their model output and focus their analysis efforts effectively.

The software supports both individual research workflows and collaborative model
development. Session persistence and state sharing capabilities facilitate
communication between team members and enable reproducible analysis workflows.
The tool has been particularly valuable for:

- Model validation and verification
- Inter-comparison studies
- Parameter sensitivity analysis
- Debugging model development issues

# Community and Sustainability

QuickView is developed as an open-source project with active collaboration
between visualization experts at Kitware, Inc. and atmospheric scientists at
Pacific Northwest National Laboratory. The project is supported by the U.S.
Department of Energy through the Scientific Discovery through Advanced Computing
(SciDAC) program, ensuring continued development and maintenance.

The software follows modern development practices including:

- Automated testing and continuous integration
- Regular releases with comprehensive documentation
- Community feedback integration through GitHub issues
- Pre-commit hooks ensuring code quality

Future development plans include support for server-client deployment on
high-performance computing systems, enhanced parallel processing capabilities,
and expansion to additional E3SM components beyond the atmospheric model.

# Conclusions

QuickView represents a successful example of domain-specific tool development
that bridges the gap between general-purpose visualization software and the
specific needs of atmospheric scientists. By providing a focused, user-friendly
interface to ParaView's powerful capabilities, the tool enables more efficient
scientific workflows and lowers barriers to advanced visualization techniques.

The tool's architecture demonstrates how modern web technologies can be
effectively combined with established scientific computing frameworks to create
accessible, powerful analysis tools. The success of QuickView in the E3SM
community suggests that similar domain-specific approaches could benefit other
areas of computational science.

# Acknowledgements

The authors acknowledge the support of the U.S. Department of Energy Office of
Science's Advanced Scientific Computing Research (ASCR) and Biological and
Environmental Research (BER) programs through the Scientific Discovery through
Advanced Computing (SciDAC) program. We thank the E3SM development team for
their feedback and testing throughout the development process.

# References
