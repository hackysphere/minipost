<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();
</script>

<h1>post {data.post.uuid}</h1>
<PostCard content={data.post} />

<style>
	h1 {
		word-break: break-all;
	}
</style>
