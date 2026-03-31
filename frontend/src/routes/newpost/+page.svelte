<script lang="ts">
	import { goto } from "$app/navigation";

	let errorValue: string | null = $state(null);
	let postContent = $state("");

	function sendPost() {
		if (postContent.trim() !== "") {
			fetch("/api/posts/new", {
				method: "POST",
				body: postContent,
			})
				.then((res) => {
					switch (res.status) {
						case 201:
							goto("/");
							break;
						case 400:
							res
								.text()
								.then(
									(err) =>
										(errorValue = `Server parsing error when sending post: ${err}`),
								)
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
	}

	addEventListener("keydown", (event) => {
		if (event.ctrlKey && event.key === "Enter") {
			sendPost();
		}
	});
</script>

<h1 style="user-select: none;">create a post</h1>
<textarea placeholder="enter your post..." bind:value={postContent}></textarea>
<button type="submit" onclick={sendPost}>publish!</button>
<span style="color: var(--ctp-mocha-subtext0)">(ctrl+enter)</span>
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
		box-sizing: border-box; /* this stops the box from overflowing into parent's margin, without doing messy stuff with maths on width */
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
