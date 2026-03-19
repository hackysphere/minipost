export const ssr = false;
export const prerender = "auto"; // if the route is static, make it return a 200 instead of falling back to the 404 method
// all this does is add more html page routes for the inital load, resources are not constantly fetched because CSR is enabled
export const trailingSlash = "always"; // get fastapi to actually serve the additional pages
