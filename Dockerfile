FROM --platform=$BUILDPLATFORM node:18 AS frontend
RUN corepack enable

WORKDIR /build

COPY nwc-frontend /build
RUN corepack prepare --activate
RUN yarn install && yarn cache clean
RUN yarn build

FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y git
RUN addgroup --system --gid 1000 web && adduser --system --uid 1000 --ingroup web --home /home/web web
RUN echo "Package: *\nPin: release a=stable-updates\nPin-Priority: 50" > /etc/apt/preferences

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pip install --upgrade pip wheel setuptools && \
    pip install --user --no-warn-script-location pipenv && \
    ~/.local/bin/pipenv install --system --deploy --ignore-pipfile --extra-pip-args=--ignore-installed && \
    rm -rf ~/.cache ~/.local


EXPOSE 8081
CMD ["gunicorn", "-b", "0.0.0.0:8081", "-k", "uvicorn.workers.UvicornWorker", "nwc_backend.server:app"]

COPY alembic.ini /app
COPY alembic /app/alembic
COPY nwc_backend /app/nwc_backend
COPY --from=frontend /build/dist/ /app/static

# Install security updates
RUN apt-get update && apt-get -y upgrade && apt-get clean && rm -rf /var/lib/apt/lists

