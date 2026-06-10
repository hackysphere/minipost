/** biome-ignore-all lint/suspicious/noFallthroughSwitchClause: svelte autobreak redirect and error functions */
import { error, redirect } from "@sveltejs/kit";
import { authState } from "$lib/AuthState.svelte";
import type { User } from "$lib/openapi/types.gen";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
	const response = await fetch("/api/account/self", {
		headers: { Authorization: `Bearer ${authState.token}` },
	});
	if (!response.ok) {
		switch (response.status) {
			case 401:
			case 403:
				redirect(303, "/auth/logout");
			default:
				error(500, "Internal server error");
		}
	}

	const user_info: User = await response.json();
	return user_info;
};
