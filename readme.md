# AIVideo

Code for AI Video generation

## Start using AIVideo

###  Run with docker

AIVideo is easy to deploy trough docker containers: one container per service

- one server monolith
- one web client node.js app

## Installation

The SDK is composed of:

- several type of videos: Composites, prompt baased video, Rawtext based videos, ...
- one type of transition, which looks a bit loke morphing
- gateways, to call models and generate videos, music, transitions, etc hosted on other platforms

### Requirements

The server components use Python and Node.js for serving
Server includes a Requirements file for python and package.json for npm
Server currently needs FFMPEG and FFPROBE

Fortunately, you just have to pull a ready to use image and run it locally using docker desktop, or run the image in the Cloud with Github codespaces.

## How to contribute

Wanna help? Wou're very welcome! First, be sure to follow those common rules:

- Submit your code using pull requests, overall we do recommand using the standard feature branch -> git merge to master cycle
- use messages as proposed here [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) when you commit your code, which refers to the [Angular](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines) types: 
  - build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
  - ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
  - docs: Documentation only changes
  - feat: A new feature
  - fix: A bug fix
  - perf: A code change that improves performance
  - refactor: A code change that neither fixes a bug nor adds a feature
  - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
  - test: Adding missing tests or correcting existing tests

- udate the changelog: [Change Log best practices](https://keepachangelog.com/en/0.3.0/)
- we do use Semantic Versionning [semantic versioning](https://semver.org/)
- use pytest for unit tests
- log is your friend, use it extensively though do use debug loglevel by default unless you really need to state something significant to an operator, be it a program or a human

Git stuff: 
- Please identify yourself with a valid email address as explained here [Setting your commit email address](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)

- Please respect the following guidelines: [Commit Message Guidelines](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines)

## What remains to be decided

- use hexagonal architecture?
        - ports
        - use cases
- use a more agent based approach?

## Support

If you have questions, reach out to us **mailing list or discusion on github**.

## Project Organisation

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

## License

_TODO Replace with your own license name and username_

To help you write a nice md : [Github MD syntax](https://docs.github.com/fr/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
