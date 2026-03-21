# build the svelte app
FROM node:24-alpine AS node

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable
WORKDIR /app/frontend

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    --mount=type=bind,source=frontend/pnpm-lock.yaml,target=pnpm-lock.yaml \
    --mount=type=bind,source=frontend/pnpm-workspace.yaml,target=pnpm-workspace.yaml \
    pnpm fetch

COPY frontend /app/frontend
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install -r --offline
RUN pnpm run build


# prepare the python backend
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS uv

ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app/backend

RUN --mount=type=cache,id=uv,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY backend /app/backend
RUN --mount=type=cache,id=uv,target=/root/.cache/uv \
    uv sync --locked

# make the final image
FROM python:3.14-alpine

COPY --from=uv /app/backend /app/backend
COPY --from=node /app/frontend/build /app/frontend/build

ENV PATH="/app/backend/.venv/bin:$PATH"

WORKDIR /app/backend

EXPOSE 8000
CMD ["fastapi", "run", "main.py"]
