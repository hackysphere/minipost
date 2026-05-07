<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { params, data }: PageProps = $props();
</script>

<!-- FIXME: this should show the username instead of the user id -->
<h1>user {params.user_id}</h1>
{#each data.posts as post (post.uuid)}
	<PostCard content={post} />
{/each}

{#if data.posts.length === 0}
	<p>no posts were found!</p>
{/if}
