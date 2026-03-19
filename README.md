# social-app
(name pending)

project that attempts to make a social media-like app  
uses python for backend and svelte for frontend  

docker deploy notes still in progress  

## basic dev notes
python steps assume you are in the backend folder  
svelte steps assume you are in the frontend folder  

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

pre-commit (global):
1. install uv
1. `uv tool install pre-commit`
1. `uv tool pre-commit install`

to manually run do `uv tool pre-commit run`

### python
install dependencies with `uv sync`  
run the dev server with `uv run fastapi dev`  
format files with `uv run ruff format`  
lint files with `uv run ruff check` (and run with the `--fix` flag to try auto-fixes)  
type check with `uv run ty check`  

### svelte
install dependencies with `pnpm install`  
run the dev server with `pnpm dev`  
format files with `pnpm format`  
lint files with `pnpm lint` (and append `:fix` to try auto-fixes)  
if svelte types are having issues, run `pnpm prepare` (using the dev server avoids this issue)  

### shared types
the backend is the source for types, svelte will inherit them through translation  
to regenerate types for svelte/typescript:
1. start the fastapi dev server
1. run `pnpm openapigen` in the backend folder

## building & running
1. run `pnpm build` in the frontend folder
1. run the app with `uv run fastapi run` in the backend folder
