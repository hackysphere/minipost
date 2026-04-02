import { error } from "@sveltejs/kit";
import type { GetLatestPostsResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
	// this is defined in an odd way because this is the main page
	// if vite's proxy breaks or something, this will show it first
	// don't do this anywhere else, assume the server is working
	let response: Response;
	try {
		response = await fetch("/api/posts");
	} catch (err) {
		console.log(err);
		error(500, "Server failed to send posts (is the backend enabled?)");
	}
	if (!response.ok) {
		error(500, "Server failed to send posts");
	}
	const latestPosts: GetLatestPostsResponse = await response.json();
	return { latest_posts: latestPosts };
};
