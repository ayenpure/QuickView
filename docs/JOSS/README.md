# JOSS Paper for QuickView

This directory contains the manuscript and supporting materials for the Journal
of Open Source Software (JOSS) submission for QuickView.

## Files

- `paper.md` - Main manuscript in JOSS format
- `paper.bib` - Bibliography file with references
- `README.md` - This file

## Paper Overview

The paper presents QuickView as an interactive visualization tool specifically
designed for atmospheric model analysis using the Energy Exascale Earth System
Model (E3SM) Atmosphere Model (EAM). The paper covers:

### Key Contributions

1. **Domain-specific visualization tool** tailored for atmospheric sciences
2. **Simplified interface** to ParaView's powerful capabilities
3. **Multi-variable analysis** with drag-and-drop interface
4. **Session persistence** for reproducible workflows
5. **Cross-platform deployment** using modern web technologies

### Technical Highlights

- Built with Python and Trame framework
- Custom ParaView plugins for EAM data handling
- Support for cubed-sphere grids and atmospheric projections
- Desktop packaging with Tauri
- Comprehensive data format support (EAM v2, v3, v4/EAMxx)

### Impact Areas

- Model validation and verification
- Inter-comparison studies
- Parameter sensitivity analysis
- Collaborative model development

## Submission Notes

### Required JOSS Elements ✓

- [x] Statement of need
- [x] Summary of functionality
- [x] Installation and usage examples (referenced from main docs)
- [x] API documentation (referenced from codebase)
- [x] Community guidelines (referenced from GitHub)
- [x] Open source license (Apache 2.0)
- [x] Automated tests (GitHub Actions)

### Author Information

- Lead author: Abhishek Yenpure (Kitware, Inc.)
- Contributing authors from Kitware and PNNL
- ORCID IDs need to be updated with actual values

### Key Metrics

- Lines of code: ~5,000+ Python
- Documentation: Comprehensive user guide and API docs
- Testing: Automated CI/CD pipeline
- Community: Active GitHub repository with issue tracking

## Next Steps

1. **Update ORCID IDs** for all authors
2. **Review technical details** for accuracy
3. **Validate references** and add any missing citations
4. **Proofread** for clarity and formatting
5. **Submit to JOSS** following their submission guidelines

## JOSS Submission Checklist

- [ ] Repository is publicly available
- [ ] License is OSI approved (Apache 2.0 ✓)
- [ ] Documentation is comprehensive
- [ ] Software has been used by multiple users
- [ ] Tests are present and passing
- [ ] ORCID IDs are provided for authors
- [ ] Paper follows JOSS format guidelines
