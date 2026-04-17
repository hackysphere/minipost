# minipost
app that posts to a temporary global timeline  
uses python for backend and svelte for frontend  

## deploying with docker
there is no image made yet, so it must be manually built by running `docker build -t minipost .`  
the image can be run with `docker run --rm -p 8000:8000 minipost`  
run with docker compose with `docker compose up -d`

TODO proxy config with docker  
TODO volumes for db

## development
### required dependencies
- uv: https://docs.astral.sh/uv/getting-started/installation)
- pnpm: https://pnpm.io/installation
- node (if using standalone pnpm, run `pnpm env use --global lts`)

### pre-commit
install uv before doing these steps  
install pre-commit hooks with `uvx pre-commit install`  
manually run hooks with `uvx pre-commit run`

### commands

|                      | python (in /backend)                           | typescript (in /frontend)                        |
| -------------------- | ---------------------------------------------- | ------------------------------------------------ |
| install dependencies | `uv sync`                                      | `pnpm install`                                   |
| dev server           | `uv run fastapi dev`                           | `pnpm dev`                                       |
| format               | `uv run ruff format`                           | `pnpm format`                                    |
| lint                 | `uv run ruff check ` (add `--fix` to auto-fix) | `pnpm lint` (append `:fix` to auto-fix)          |
| type check           | `uv run ty check`                              | `pnpm check`                                     |

### shared types
the backend is the source for types, the frontend will inherit them through translation  
to regenerate types for typescript:
1. start the fastapi dev server
1. run `pnpm openapigen` in the backend folder

## building & running
1. run `pnpm build` in the frontend folder
1. run the app with `uv run -m app.main` in the backend folder
    * using `uv run fastapi run` will assume that you are behind a proxy, add `--no-proxy-headers` to disable this
      this is why running with `app.main` is recommended, as it follows the config file
