import adapter from "@sveltejs/adapter-static";

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			// fastapi will serve a 404.html if there are no routes found, so dynamic routes can actually be done in a wonky way
			// (it will still return a 404 for the html, but everything else will be fine)
			fallback: "404.html",
		}),
	},
};

export default config;
