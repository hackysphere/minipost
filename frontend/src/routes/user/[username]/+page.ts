import type { GetPostsFromUserResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, params }) => {
	const response: GetPostsFromUserResponse = await (
		await fetch(`/api/users/${params.username}/posts`)
	).json();
	return { posts: response };
};
