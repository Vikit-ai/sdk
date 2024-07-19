.. .. _contributing:

============
Contributing
============

Wanna help? You're very welcome! A typical Pull Request workflow would be like this:
1. New PR: You submit your PR.
2. PR validation: If the PR passes all the quality checks then Vikit.ai team assign a reviewer. We may ask for additional changes to make to PR pass quality checks.
3. PR review: If everything looks good, the reviewer(s) will approve the PR. The reviewers might ask some modifications before approving your PR.
4. CI tests & Merge: Once the PR is approved we launch CI tests. We may ask further modifications in this step, in order to get all the tests passed before merging your PR. Once all the tests pass, vikit team merge the code internally as well as externally on GitHub.

How to contribute?
------------------
- Fork vikit repository into your own GitHub account.
- Create a new branch and make your changes to the code.
- Commit your changes and push the branch to your forked repository.
- Open a pull request on our repository.

General guidelines and standards
--------------------------------
Please make sure your changes are consistent with these common guidelines:

- Include unit tests when you contribute new features
- Keep API compatibility in mind when you change code 
- Use messages as proposed in `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_ when you commit your code, which refers to the `Angular types <https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines>`_:

  - build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
  - ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
  - docs: Documentation only changes
  - feat: A new feature
  - fix: A bug fix
  - perf: A code change that improves performance
  - refactor: A code change that neither fixes a bug nor adds a feature
  - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
  - test: Adding missing tests or correcting existing tests

- Update the changelog: `Change Log best practices <https://keepachangelog.com/en/0.3.0/>`_
- We do use Semantic Versioning `semantic versioning <https://semver.org/>`_
- Please identify yourself with a valid email address as explained in `Setting your commit email address <https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address>`_
