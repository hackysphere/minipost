<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();
</script>

<h1>post <span class="uuid">{data.post.uuid}</span></h1>
<PostCard content={data.post} />
{#if data.post.replies}
	<hr>
	{#each data.post.replies as reply (reply.uuid)}
		<PostCard content={reply} reply={true} />
	{/each}
{/if}

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
