<script lang="ts">
	import { goto } from "$app/navigation";
	import { rootURL } from "$lib/constants";

	let errorValue: string | null = $state(null);
	let postContent = $state("");

	function sendPost(): void {
		if (postContent !== "") {
			fetch(`${rootURL}/api/posts/new`, {
				method: "POST",
				body: postContent,
			})
				.then(() => {
					goto("/");
				})
				.catch((err) => {
					errorValue = err;
				});
		}
	}
</script>

<h1>create a post</h1>
<textarea placeholder="enter your post..." bind:value={postContent}></textarea>
<button type="submit" onclick={sendPost}>publish!</button>
{#if errorValue}
	<p class="error">Error when sending post: {errorValue}</p>
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
