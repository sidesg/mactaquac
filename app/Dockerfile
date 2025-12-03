FROM python:3.14-slim-trixie as base

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Instal uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

# Instal dependancies
WORKDIR /app
COPY pyproject.toml uv.lock ./
# RUN uv sync --frozen --no-dev --python /usr/local/bin/python3 \
#     && rm -rf /root/.cache/uv

RUN uv sync --frozen --compile-bytecode

FROM python:3.14-slim-trixie as final
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN addgroup --system app && adduser --system --group app

RUN mkdir -p /home/app
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY --from=base /bin/uv /usr/local/bin/uv
COPY --from=base /app/.venv $APP_HOME/.venv
COPY --from=base /app $APP_HOME

RUN chown -R app:app $HOME
USER app

# Copy the project into the image
ADD . $APP_HOME

CMD [ "uv", "run", "gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000" ]
