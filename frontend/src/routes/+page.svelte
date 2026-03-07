<script lang="ts">
	// TODO: move this to +page.ts
	import PostCard from "$lib/PostCard.svelte";
	let posts: string[] = $state([]);
</script>

<h1>homepage</h1>

<div>
	<h2>debug</h2>
	<button class="additive" onclick={() => posts.push(Date.now().toString())}>add post</button>
	<button class="destructive" onclick={() => posts.shift()}>delete first post</button>
	<button class="destructive" onclick={() => posts.pop()}>delete last post</button>
	<button class="destructive" onclick={() => posts = []}>delete ALL posts</button>
</div>

{#each posts as post}
	<PostCard content={post} />
{/each}

<style>
	button {
		background-color: hsl(237deg, 16%, 23%);
		color: hsl(226deg, 64%, 88%);
		border: none;
		padding: 4px;
		border-radius: 5px;
	}

	button:hover {
		background-color: hsl(234deg, 13%, 31%);
	}
	button:active {
		background-color: hsl(233deg, 12%, 39%);
	}
	button.additive {
		background-color: hsl(115deg, 54%, 76%);
		color: hsl(240deg, 23%, 9%);
	}
	button.destructive {
		background-color: hsl(343deg, 81%, 75%);
		color: hsl(240deg, 23%, 9%);
	}
</style>
