import { getConfig } from "src/utils/getConfig";

export enum Routes {
  Root = "/",
  Connection = "/connection",
  ConnectionNew = "/connection/new",
  ConnectionDetail = "/connection/:connectionId",
  ConnectionUpdate = "/connection/:connectionId/update",
  AppsNew = "/apps/new",
}

type PathParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | PathParams<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

type RouteParams<Route extends Routes> = PathParams<Route>;

export type Path = string;

export function generatePath<Route extends Routes>(
  route: Route,
  params: Record<RouteParams<Route>, string>,
): Path {
  const basePath = getConfig().basePath;
  return (
    basePath +
    Object.entries(params).reduce<string>(
      (path, [param, value]) => path.replace(`:${param}`, String(value)),
      route,
    )
  );
}
