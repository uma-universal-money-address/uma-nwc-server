# NWC frontend

This is a frontend app for managing UMA Auth connections and permissions.

## Local development

```
yarn install
```

```
yarn dev
```

Navigate to `http://localhost:8080`

## Build

```
yarn build
```

## Deployment

This app is served alongside the backend in `nwc-backend`. The frontend is built as a single-page application (SPA) and the backend contains a catchall route to serve any frontend-related files.

## Testing the build being served from the backend

> ⚠️ Warning: Only do this if you're debugging specific deployment issues with how frontend files are being served.
> This is not recommended for normal local development.

Since we are deploying the frontend and backend in the same docker image,
and they will be served with the same domain, the backend serves the frontend build files. This is accomplished with a catch-all route in the Quart server
which serves any static files if they exist, or the index.html file. The `nwc_backend/configs/local_dev.py` config looks for the
build folder (dist) via a relative path, so make sure to update that if the build folder
or uma-dogfood-app folder's names are changed.

To test this locally, you must:

1. Follow the setup instructions in the root `README.md`
1. Build with `yarn build` from the `nwc-frontend` directory.
1. Start the backend in the root directory with `FLASK_CONFIG="local_dev.py" flask run`
1. Navigate to `http://localhost:8080`.

Now both frontend files and the API will be served by the same URL `http://localhost:8080`!
