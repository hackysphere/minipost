/** biome-ignore-all lint/suspicious/noFallthroughSwitchClause: biome does not correctly detect svelte error() escaping the switch statement */
import { error } from "@sveltejs/kit";
import type {
	GetPostsByUseridResponse,
	GetUserResponse,
} from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, params }) => {
	const user_response = await fetch(`/api/users/${params.user_id}`);
	if (!user_response.ok) {
		switch (user_response.status) {
			case 404:
				error(404, "User not found");
			case 422:
				error(422, "Invalid user id");
			default:
				error(500, "Internal server error");
		}
	}

	const posts_response = await fetch(`/api/users/${params.user_id}/posts`);
	if (!posts_response.ok) {
		switch (posts_response.status) {
			case 404:
				error(404, "User not found");
			case 422:
				error(422, "Invalid user id");
			default:
				error(500, "Internal server error");
		}
	}

	const posts: GetPostsByUseridResponse = await posts_response.json();
	const user: GetUserResponse = await user_response.json();
	return { user, posts };
};
