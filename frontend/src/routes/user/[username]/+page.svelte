<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { params, data }: PageProps = $props();
</script>

<h1>user {params.username}</h1>
{#each data.posts as post (post.uuid)}
	<PostCard content={post} />
{/each}

{#if data.posts.length === 0}
	<p>no posts were found!</p>
{/if}
