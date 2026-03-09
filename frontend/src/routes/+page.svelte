<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();
</script>

<h1>global timeline</h1>

{#each data.latest_posts as post}
	<PostCard content={post} />
{/each}

<style>
	h1 {
		padding-left: 4rem;
	}
</style>
