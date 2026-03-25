FROM python:3.13-slim-trixie AS base

ENV UV_NO_DEV=1
ENV UV_COMPILE_BYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.11.0 /uv /uvx /usr/local/bin/

WORKDIR /home/app/web

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-install-project


FROM python:3.13-slim-trixie AS final

RUN addgroup --system app && adduser --system --group app

RUN mkdir -p /home/app
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY --from=base /home/app/web $APP_HOME

ENV PATH="$APP_HOME/.venv/bin:/usr/local/bin:/usr/bin:/bin"

COPY . $APP_HOME

RUN chown -R app:app $HOME
USER app

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]