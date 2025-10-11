FROM python:3.14-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable uv optimizations:
# UV_LINK_MODE=copy ensures dependencies are copied (isolated env)
ENV UV_LINK_MODE=copy

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
# The "cache" mount allows efficient reuse of a uv cache on rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project

# Copy the project into the image
COPY . .

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen

CMD ["uv", "run", "uvicorn", "deadlock_assets_api.main:app", "--host", "0.0.0.0"]
