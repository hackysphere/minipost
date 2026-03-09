import type { GetLatestPostsResponse } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { rootURL } from "$lib/constants";

export const load: PageLoad = async ({ fetch, params }) => {
  let response: Response;
  try {
    response = await fetch(rootURL + "api/posts/latest");
  } catch (err) {
    console.log(err);
    error(404, "Failed to fetch latest posts, you might be offline?");
  }
  const latest_posts: GetLatestPostsResponse = await response.json();
  return { latest_posts };
};
