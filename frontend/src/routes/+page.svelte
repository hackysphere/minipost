<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();
</script>

<h1 style="user-select: none;">global timeline</h1>

{#each data.latest_posts as post (post.uuid)}
	<PostCard content={post} />
{/each}

{#if data.latest_posts.length === 0}
	<p>there are no posts!</p>
{/if}
