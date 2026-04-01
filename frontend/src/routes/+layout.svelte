<script lang="ts">
	import favicon from "$lib/assets/favicon.svg";
	import "./global.css";

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon}>
	<title>minipost</title>
</svelte:head>

<style>
	:global(html) {
		background-color: var(--ctp-mocha-base);
		color: var(--ctp-mocha-text);
		font-family: Inter, sans-serif;
	}
	:global(a) {
		color: var(--ctp-mocha-sapphire);
	}
	:global(a:hover) {
		color: var(--ctp-mocha-blue);
	}
	:global(h1) {
		user-select: none;
	}

	:root {
		max-width: 750px;
		margin: 0 auto;
	}

	nav {
		padding: 5px 0px;
		border-style: solid;
		border-color: var(--ctp-mocha-teal);
		border-width: 0 0 5px;
		font-weight: 600;
		user-select: none;
		display: flex;
		justify-content: space-between;
	}
	nav div {
		display: inline-flex;
	}

	nav div * {
		margin: 0px 7px;
	}
	nav div *:first-child {
		margin: 0px;
	}
	nav a {
		text-decoration-line: none;
		color: var(--ctp-mocha-teal);
		transition-duration: 100ms;
	}
	nav a:hover {
		color: var(--ctp-mocha-green);
	}

	nav .logo-link {
		color: var(--ctp-mocha-text);
		display: flex;
	}
	nav .logo-link:hover {
		color: var(--ctp-mocha-subtext0);
	}
</style>

<nav>
	<div>
		<a href="/" class="logo-link">
			<img src={favicon} alt="">
			<span>minipost</span>
		</a>
		<a href="/newpost">post</a>
		<a href="/about">about</a>
	</div>
</nav>

{@render children()}
