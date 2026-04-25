<script lang="ts">
	import { goto } from "$app/navigation";
	import PostInput from "$lib/PostInput.svelte";

	let errorValue: string | undefined = $state();

	function sendPost(postContent: string, postUsername: string) {
		fetch("/api/posts", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				content: postContent,
				username: postUsername,
			}),
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
					default:
						errorValue = "Error submitting post";
				}
			})
			.catch(() => {
				errorValue = "Failed to submit post, server may be offline";
			});
	}
</script>

<h1>create a post</h1>
<PostInput callback={sendPost} error={errorValue} />
