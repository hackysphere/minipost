/** biome-ignore-all lint/suspicious/noFallthroughSwitchClause: biome does not correctly detect svelte error() escaping the switch statement */
import { error } from "@sveltejs/kit";
import type { GetPostsFromUseridResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, params }) => {
	const response = await fetch(`/api/users/${params.user_id}/posts`);
	if (!response.ok) {
		switch (response.status) {
			case 404:
				error(404, "User not found");
			case 422:
				error(422, "Invalid user id");
			default:
				error(500, "Internal server error");
		}
	}

	const posts: GetPostsFromUseridResponse = await response.json();
	return { posts };
};
