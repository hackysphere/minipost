/** biome-ignore-all lint/suspicious/noFallthroughSwitchClause: biome does not correctly detect svelte error() escaping the switch statement */
import { error } from "@sveltejs/kit";
import type { GetPostResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, params }) => {
	const response = await fetch(`/api/posts/${params.post_uuid}`);
	if (!response.ok) {
		switch (response.status) {
			case 404:
				error(404, "Post not found");
			case 422:
				error(422, "Invalid post ID");
			default:
				error(500, "Internal server error");
		}
	}

	const post: GetPostResponse = await response.json();
	return { post };
};
