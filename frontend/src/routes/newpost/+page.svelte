<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { authState } from "$lib/AuthState.svelte";
	import type { BodyCreatePost } from "$lib/openapi/types.gen";
	import PostInput from "$lib/PostInput.svelte";

	let errorValue: string | undefined = $state();

	function sendPost(postContent: string) {
		let body: BodyCreatePost = {
			body: postContent,
		};

		fetch("/api/posts", {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
				Authorization: `Bearer ${authState.token}`,
			},
			body: new URLSearchParams(body),
		})
			.then((res) => {
				switch (res.status) {
					case 201:
						goto("/");
						break;
					case 400:
						res
							.text()
							.then((err_response) => {
								let jsonerr = JSON.parse(err_response);
								errorValue = `Server parsing error when sending post: ${jsonerr.detail}`;
							})
							.catch(
								() => (errorValue = "Server parsing error when sending post"),
							);
						break;
					case 401:
					case 403:
						goto("/auth/logout");
						break;
					default:
						errorValue = "Error submitting post";
				}
			})
			.catch(() => {
				errorValue = "Failed to submit post, server may be offline";
			});
	}

	onMount(() => {
		if (authState.token === "") {
			goto("/auth", { replaceState: true });
		}
	});
</script>

<h1>create a post</h1>
<PostInput callback={sendPost} error={errorValue} />
