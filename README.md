<h1 align="center">
  <br>
  <img src="images/opsml-artifacts-logo.png"  width="536" height="230" alt="py opsml logo"/>
  <br>
</h1>

<h4 align="center">Trading cards for machine learning workflows.</h4>

<p align="center">
  <a href="https://drone.shipt.com/shipt/py-opsml">
  <img alt="Build Status" src="https://drone.shipt.com/api/badges/shipt/opsml-data/status.svg"/>

  <a href="https://www.python.org/downloads/release/python-390/">
  <img alt="Python" src="https://upload.wikimedia.org/wikipedia/commons/1/1b/Blue_Python_3.9_Shield_Badge.svg" />

  <img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg" />

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="quality gate" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=alert_status&token=squ_06f8921843044242e5975ed012023f7b09066e9c" />

  <a href="https://sonarqube.shipt.com/dashboard?id=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq">
  <img alt="coverage" src="https://sonarqube.shipt.com/api/project_badges/measure?project=shipt_opsml-artifacts_AYWcv6FFE00GGQFT3YPq&metric=coverage&token=squ_06f8921843044242e5975ed012023f7b09066e9c" />
</p>

<p align="center">
  <a href="#key-features">What is it?</a> •
  <a href="#how-to-use">Features</a> •
  <a href="#download">Download</a> •
  <a href="#credits">Credits</a> •
  <a href="#related">Related</a> •
  <a href="#license">License</a>
</p>

## What is it?

`OpsML-Artifacts` is a library for tracking,  storing, versioning, and reproducing artifacts (aka Artifact Cards) across the ML-lifecycle. Think of it as trading cards for machine learning.

<p align="center">
  <img src="images/artifacts-diagram.png"  width="480" height="400" alt="py opsml logo"/>
</p>

## Features:
  - Simple Design:  Standardized design for all card types and registries to make switching between and registering different types easy.

  - Automation: Automatic type checking for card attributes. Automated processes depending on card type (Onnx conversion for model, api signature generation, data schema creation)

  - Short: Easy to integrate into your existing workflows. You just need a card type and a registry to get started

