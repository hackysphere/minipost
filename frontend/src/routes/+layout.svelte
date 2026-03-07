<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<style>
	/* all using catppuccin mocha colors */
	/* TODO: set up better color selection (either vars or js module) */
	:global(html) {
		background-color: hsl(240deg, 21%, 15%);
		color: hsl(226deg, 64%, 88%);
		font-family: Inter, sans-serif;
	}
	:global(a) {
		color: hsl(199deg, 76%, 69%);
	}

	#app {
		max-width: 750px;
		margin: 0 auto;
	}

	nav {
		padding: 5px;
		border-style: solid;
		border-color: hsl(170deg, 57%, 73%);
		border-width: 0 0 5px;
		font-weight: 600;
	}
	
	nav a {
		text-decoration-line: none;
		color: hsl(170deg, 57%, 73%);
	}
</style>

<div id="app">
	<nav>
		<a href="/">home</a>
	</nav>

	{@render children()}
</div>
