# NWC frontend

This is a frontend app for managing UMA Auth connections and permissions.

## Local development

```
yarn install
```

```
yarn dev
```

Navigate to `http://localhost:3000`

## Build

```
yarn build
```

## Deployment

This app is served alongside the backend in `nwc-backend`. The frontend is built as a single-page application (SPA) and the backend contains a catchall route to serve any frontend-related files.
