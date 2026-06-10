<script lang="ts">
	import { authState } from "$lib/AuthState.svelte";
	import favicon from "$lib/assets/favicon.svg";
	import "./global.css";

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon}>
	<title>minipost</title>
</svelte:head>

<style>
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
		--font-body: SpaceGrotesk, sans-serif;
		--font-mono: JetBrainsMono, monospace;
		max-width: 800px;
		margin: 0 auto;
		background-color: var(--ctp-mocha-base);
		color: var(--ctp-mocha-text);
		font-family: var(--font-body);
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
		/* using rem/em here preserves spacing when changing root font size */
		margin: 0 0.4em;
	}
	nav div.maincontent *:first-child {
		margin: 0px;
	}
	nav div.accountcontent *:last-child {
		margin-right: 0;
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
		align-items: center;
	}
	nav .logo-link:hover {
		color: var(--ctp-mocha-subtext0);
	}
	nav .logo-link img {
		height: 1em;
	}
</style>

<nav>
	<div class="maincontent">
		<a href="/" class="logo-link">
			<img src={favicon} alt="">
			<span>minipost</span>
		</a>
		<a href="/newpost">post</a>
		{#if authState.token}
			<a href={`/user/${authState.user_id}`}>me!</a>
		{/if}
		<a href="/about">about</a>
	</div>
	<div class="accountcontent">
		{#if authState.token}
			<a href="/account">account</a>
			<a href="/auth/logout">logout</a>
		{:else}
			<a href="/auth">login</a>
		{/if}
	</div>
</nav>

{@render children()}
