import { error } from "@sveltejs/kit";
import type { GetLatestPostsResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

// supports the params parameter, but since it is unused, biome wants me to remove it
export const load: PageLoad = async ({ fetch }) => {
	let response: Response;
	try {
		response = await fetch("/api/posts/latest");
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
