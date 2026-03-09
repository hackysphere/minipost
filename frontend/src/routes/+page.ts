import type { GetLatestPostsResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch, params }) => {
  const response = await fetch("http://localhost:8000/api/posts/latest");
  const latest_posts: GetLatestPostsResponse = await response.json();
  return { latest_posts };
};
