<script lang="ts">
	import favicon from "$lib/assets/favicon.svg";
	import "./global.css";

	let { children } = $props();
</script>

<svelte:head> <link rel="icon" href={favicon}> </svelte:head>

<style>
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

	nav * {
		margin: 0px 7px;
	}

	nav a {
		text-decoration-line: none;
		color: var(--ctp-mocha-teal);
		transition-duration: 100ms;
	}
	nav a:hover {
		color: var(--ctp-mocha-green);
	}
</style>

<div id="app">
	<nav>
		<span>social-app--frontend</span>
		<a href="/">home</a>
		<a href="/newpost">post</a>
	</nav>

	{@render children()}
</div>
