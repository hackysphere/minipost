<script lang="ts">
	import favicon from "$lib/assets/favicon.svg";
	import "./global.css"

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<style>
	/* all using catppuccin mocha colors */
	/* TODO: set up better color selection (either vars or js module) */
	:global(html) {
		background-color: var(--ctp-mocha-base);
		color: var(--ctp-mocha-text);
		font-family: Inter, sans-serif;
	}
	:global(a) {
		color: var(--ctp-mocha-sapphire);
	}

	#app {
		max-width: 750px;
		margin: 0 auto;
	}

	nav {
		padding: 5px;
		border-style: solid;
		border-color: var(--ctp-mocha-teal);
		border-width: 0 0 5px;
		font-weight: 600;
	}
	
	nav a {
		text-decoration-line: none;
		color: var(--ctp-mocha-teal);
	}
</style>

<div id="app">
	<nav>
		<a href="/">home</a>
	</nav>

	{@render children()}
</div>
