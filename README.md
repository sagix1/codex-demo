# Codex Demo

This repository contains small Python utilities, including a static file web
server with basic security and error handling.

## Static File Server

`server.py` starts a multithreaded HTTP server that serves files from a chosen
directory (current directory by default). It performs the following safeguards:

- Rejects attempts to access files outside of the configured directory.
- Prevents directory listings unless an `index.html` file is present.
- Returns descriptive HTTP error responses for missing or unreadable files.
- Logs each request and captures internal server errors for easier debugging.

### Usage

```bash
python server.py --host 127.0.0.1 --port 8000 --directory .
```

Press `Ctrl+C` to stop the server.

### Working with Git

This project currently has no remotes configured (`git remote -v` prints
nothing). To publish your local commits, add a remote and push explicitly, for
example:

```bash
git remote add origin git@github.com:username/repository.git
git push -u origin work
```

The examples assume that the active branch is `work`; adjust the branch name to
match your local checkout.

## Repository Structure Analysis

Current layout:

```
.
├── README.md
├── hello.py
└── server.py
```

### Suggested Improvements

- **Organize scripts**: Move executable Python scripts into a `src/` or
  `scripts/` directory to clearly separate source code from documentation.
- **Add tests**: Introduce automated tests (for example using `pytest`) to
  exercise server functionality and prevent regressions.
- **Automate linting**: Configure formatting and linting tools (such as
  `black`, `ruff`, or `flake8`) to enforce consistent style.
- **Package metadata**: If the project grows, consider adding a `pyproject.toml`
  file to manage dependencies and entry points.
- **CI integration**: Set up a continuous integration workflow (GitHub Actions
  or similar) to run tests and linting automatically on each change.
