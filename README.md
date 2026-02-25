# social-app
(name pending)

project that attempts to make a social media-like app  
uses python for backend and svelte for frontend

dev notes still in progress  
docker deploy notes still in progress

## basic dev notes
### required dependencies
python:
- uv
    - [install manually](https://docs.astral.sh/uv/getting-started/installation) *or*
    - install through pip: `pip install uv` or `pipx install uv` (not tested)

svelte:
- pnpm
    - [install manually](https://pnpm.io/installation) *or*
    - install through npm: `npm install -g pnpm@latest-10` (not tested) *or*
    - install through corepack: (not tested)
        1. run `npm install --global corepack@latest`
        1. run `corepack enable pnpm`

### project setup
python:
1. enter the backend folder
1. run `uv sync`

svelte:
1. enter the frontend folder
1. run `pnpm i`

### formatting and linting
(no pre-commit hooks yet)

python:
1. enter the backend folder
1. run `uv run ruff check`
1. run `uv run ty check`

svelte:
1. enter the frontend folder
1. run `pnpm lint`
    - if errors are found, try `pnpm lint:fix` to try to fix them automatically
1. run `pnpm fmt`
