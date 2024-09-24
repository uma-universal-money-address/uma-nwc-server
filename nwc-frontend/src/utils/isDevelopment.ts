 // @ts-expect-error - process is showing up as undefined.
const isDevelopment = process?.env?.NODE_ENV === "development";
export default isDevelopment;
