<script lang="ts">
	import PostCard from "$lib/PostCard.svelte";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();
</script>

<h1>post {data.uuid}</h1>
<PostCard content={data} />
