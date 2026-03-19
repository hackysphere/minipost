import adapter from "@sveltejs/adapter-static";

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			// fastapi will serve a 404.html if there are no routes found
			// this makes all routes go through the 404, which means sveltekit can successfully do CSR!!
			// this also allows for dynamic routes
			// this does not affect anything, as prerendering without SSR will give the same "shell" pages as the 404.html
			fallback: "404.html",
		}),
	},
};

export default config;
