# Contributing to demml/opsml

## Welcome
Hello! We're glad and grateful that you're interested in contributing to `OpsML` :tada:! Below you will find the general guidelines for setting up your environment and creating/submitting `pull requests`.

## Very Important
To contribute to `OpsML` you will need to sign a Contributor License Agreement (CLA) via HelloSign when you create your first `pull_request` (this is an automated process). For a `pull_request` to be valid, your Github email address must match the email address used to sign the CLA. Github has [documentation](https://help.github.com/articles/setting-your-commit-email-address-on-github/) on setting email addresses. Your git email must also match this email address


## Table of contents

- [Environment setup](#environment-setup)
- [Contributing changes](#contributing-changes)
- [Contributing TLDR](#contributing-tldr)
- [Community guidelines](#community-guidelines)
- [Reporting bugs](#submitting-issues/bugs)
- [Suggesting enhancements](#suggesting-enhancements)


## Environment Setup
Steps:
1. Create a new env. `OpsML` currently supports python 3.9 -> 3.11
2. Fork `OpsML`
3. Install all required and development packages in your new env (we use [poetry](https://github.com/python-poetry/poetry) for dependency management).

```bash
make setup
```
or with poetry directly

```bash
poetry install --all-extras --with dev,dev-lints
```

## Contributing Changes
1. Create a new branch for your addition
   * General naming conventions (we're not picky):
      * `/username/<featureName>`: for features
      * `/username/<fixName>`: for general refactoring or bug fixes
2. Test your changes:
   * You can run formatting, lints and tests locally via `make format`, `make lints` and `make unit.tests`, respectively.
3. Submit a Draft Pull Request. Do it early and mark it `WIP` so a maintainer knows it's not ready for review just yet. You can also add a label to it if you feel like it :smile:.
4. If you haven't signed our CLA before, then you will receive an email from HelloSign to sign the CLA (mentioned above).
    * The CLA request will be sent to the email address associated with your github account.
    * You cannot have your PR merged without signing the PR.
    * If you already submitted a PR and need to correct your user.name and/or user.email please do so and then use `git commit --amend --reset-author` and then `git push --force` to correct the PR.
5. Move the `pull_request` out of draft state.
   * Make sure you fill out the `pull_request` template (included with every `pull_request`)
6. Request review from one of our maintainers (this should happen automatically via `.github/CODEOWNERS`). 
7. Get Approval. We'll let you know if there are any changes that are needed. 
8. Merge your changes into `OpsML`!

## Contributing TLDR
1. Create branch
2. Add changes
3. Test locally
4. Create PR (fill out CLA if you haven't before)
5. Get your awesome work reviewed and approved by a maintainer
6. Merge
7. Celebrate!

## Community Guidelines
  1. Be Kind
    - Working with us should be a fun learning opportunity, and we want it to be a good experience for everyone. Please treat each other with respect.  
    - If something looks outdated or incorrect, please let us know! We want to make `OpsML` as useful as possible. 
  2. Own Your Work
     * Creating a PR for `OpsML` is your first step to becoming a contributor, so make sure that you own your changes. 
     * Our maintainers will do their best to respond to you in a timely manner, but we ask the same from you as the contributor. 

## Submitting issues/bugs

We use [GitHub issues](https://github.com/thorrester/opsml/issues) to track bugs and suggested enhancements. You can report a bug by opening a new issue [new issue](https://github.com/demml/opsml/issues/new/choose) Before reporting a bug/issue, please check that it has not already been reported, and that it is not already fixed in the latest version. If you find a closed issue related to your current issue, please open a new issue and include a link to the original issue in the body of your new one. Please include as much information about your bug as possible.

## Suggesting enhancements

You can suggest an enhancement by opening a [new feature request](https://github.com/demml/opsml/issues/new?labels=enhancement&template=feature_request.yml).
Before creating an enhancement suggestion, please check that a similar issue does not already exist.

Please describe the behavior you want and why, and provide examples of how `OpsML` would be used if your feature were added.

## _Thank you!_