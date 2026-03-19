<script lang="ts">
	import { goto } from "$app/navigation";
	import { rootURL } from "$lib/constants";

	let errorValue: string | null = $state(null);
	let postContent = $state("");

	// biome-ignore lint/correctness/noUnusedVariables: biome is not detecting usage in svelte property
	function sendPost() {
		if (postContent.trim() !== "") {
			fetch(`${rootURL}/api/posts/new`, {
				method: "POST",
				body: postContent,
			})
				.then((res) => {
					switch (res.status) {
						case 201:
							goto("/");
							break;
						case 400:
							res.text()
								.then((err) => errorValue = `Parsing error: ${err}`)
								.catch(() => errorValue = "Parsing error when sending post");
							break;
						default:
							errorValue = "Error submitting post";
					}
				})
				.catch(() => {
					errorValue = "Failed to submit post, server may be offline";
				});
		}
	}
</script>

<h1>create a post</h1>
<textarea placeholder="enter your post..." bind:value={postContent}></textarea>
<button type="submit" onclick={sendPost}>publish!</button>
{#if errorValue}
	<p class="error">{errorValue}</p>
{/if}

<style>
	textarea {
		font-family: Inter, sans-serif;
		background-color: var(--ctp-mocha-surface1);
		color: var(--ctp-mocha-text);
		width: 100%;
		resize: none;
		border: none;
		padding: 10px;
		border-radius: 5px;
	}
	button {
		margin: 10px;
		margin-left: 0px;
		padding: 7px;
		font-size: 1.2rem;
		border-radius: 7px;
		border: none;
		background-color: var(--ctp-mocha-green);
		color: var(--ctp-mocha-base);
	}
	.error {
		color: var(--ctp-mocha-maroon);
	}
</style>
