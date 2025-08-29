<h1 align="center">
  <br>
  <img src="https://github.com/demml/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

# OpsML: Quality Control for the Machine Learning Lifecycle

<h2 align="center">OSS Version 3.0.0 Coming Soon!</h2>

## **Note from maintainers**

Version 3.0.0 is under active development. All pre-releases will be released under the `3.0.0-rc.*` tag.

<h1 align="center"><a href="https://demml.github.io/opsml/">OpsML Documentation</h1>

<h2 align="center"><a href="https://github.com/orgs/demml/projects/1">Task Backlog</h2>

[![OpsML Unit Tests](https://github.com/demml/opsml/actions/workflows/lints-test.yml/badge.svg)](https://github.com/demml/opsml/actions/workflows/lints-test.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

## **What is it?**

`OpsML` is a developer-first ML operations platform focused on injecting quality control into the machine learning lifecycle. Through automation and standardization, `OpsML` provides a unified interface and experience for managing ML artifacts, enabling teams to collaborate more effectively and deploy with confidence, all while reducing engineering overhead and providing peace of mind.

## **What is Quality Control?**

Quality control in the context of `OpsML` refers to:

### Developer-First Experience
- **Zero-friction Integration** - Drop into existing ML workflows in minutes
- **Type-safe by Design** - Rust in the back, python in the front<sup>*</sup>. Catch errors before they hit production
- **Unified API** - One consistent interface for all ML frameworks
- **Environment Parity** - Same experience from laptop to production
- **Dependency Overhead** - One dependency for all ML artifact management

### Built to Scale
- **Trading Cards for ML** - Manage ML artifacts like trading cards - collect, organize, share
- **Cloud-Ready** - Native support for AWS, GCP, Azure
- **Modular Design** - Use what you need, leave what you don't

### Production Ready
- **High-Performance Server** - Built in Rust for speed, reliability, and concurrency
- **Built-in Security** - Authentication and encryption out of the box
- **Audit-Ready** - Complete artifact lineage and versioning
- **Standardized Governance** - Consistent patterns across teams
- **Built-in Monitoring** - Integrated with Scouter
  
<sup>
OpsML is written in Rust and is exposed via a Python API built with PyO3.
</sup>

### Us vs Others

| Feature | OpsML | Others |
|---------|:-------:|:--------:|
| **Artifact-First Approach** | ✅ | ❌ |
| **SemVer for All Artifacts** | ✅ | ❌ (rare) |
| **Multi-Cloud Compatibility** | ✅ | ✅ |
| **Multi-Database Support** | ✅ | ✅ |
| **Authentication** | ✅ | ✅ |
| **Encryption** | ✅ | ❌ (rare) |
| **Artifact Lineage** | ✅ | ❌ (uncommon) |
| **Out-of-the-Box Model Monitoring & Data Profiling** | ✅ | ❌ |
| **Isolated Environments (No Staging/Prod Conflicts)** | ✅ | ❌ |
| **Single Dependency** | ✅ | ❌ |
| **Low-friction Integration Into Your Current Tech Stack** | ✅ | ❌ |
| **Standardized Patterns and Workflows** | ✅ | ❌ |
| **Open Source** | ✅ | ❌ (some) |

## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started.

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) for creating a great foundation to build from!
