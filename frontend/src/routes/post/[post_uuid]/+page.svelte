<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import PostCard from "$lib/PostCard.svelte";
	import PostInput from "$lib/PostInput.svelte";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();

	let sendPostError: string | undefined = $state();
	function sendPost(content: string, username: string) {
		fetch(`/api/posts/${data.post.uuid}/reply`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				content: content,
				username: username,
			}),
		})
			.then((res) => {
				switch (res.status) {
					case 201:
						invalidateAll();
						break;
					case 400:
						res
							.text()
							.then((err_response) => {
								sendPostError = `Server parsing error when sending post: ${JSON.parse(err_response).detail}`;
							})
							.catch(() => {
								sendPostError = "Server parsing error when sending post";
							});
						break;
					default:
						sendPostError = "Error submitting post";
				}
			})
			.catch(() => {
				sendPostError = "Failed to submit post, server may be offline";
			});
	}
</script>

<h1>post <span class="uuid">{data.post.uuid}</span></h1>
<PostCard content={data.post} basecontent={true} />
{#if data.post.replies}
	<hr>
	{#each data.post.replies as reply (reply.uuid)}
		<PostCard content={reply} reply={true} />
	{/each}
{/if}
<hr>
<PostInput callback={sendPost} error={sendPostError} />

<style>
	h1 {
		word-break: break-all;
	}

	hr {
		margin: 20px 0;
		color: #0000;
	}

	.uuid {
		font-family: JetBrainsMono, monospace;
	}
</style>
