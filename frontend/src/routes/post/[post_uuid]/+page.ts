import type { GetPostByUuidResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, params }) => {
	const response: GetPostByUuidResponse = await (
		await fetch(`/api/posts/${params.post_uuid}`)
	).json();
	return response;
};
