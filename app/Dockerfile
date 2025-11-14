FROM python:3.14-slim-trixie

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

# drop to unprivileged user
RUN useradd --create-home appuser
RUN mkdir -p /app  # has this already been created?
RUN chown --recursive appuser:root /app
WORKDIR /app
USER appuser

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

CMD [ "uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000" ]