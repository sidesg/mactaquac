FROM python:3.14-slim-trixie

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Instal uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /uvx /bin/

RUN addgroup --system app && adduser --system --group app

RUN mkdir -p /home/app
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN chown -R app:app $HOME
WORKDIR $APP_HOME
USER app

# Copy the project into the image
ADD . $APP_HOME

WORKDIR $APP_HOME
RUN uv sync --locked

CMD [ "uv", "run", "gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000" ]
