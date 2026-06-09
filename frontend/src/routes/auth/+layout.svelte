<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { authState } from "$lib/AuthState.svelte";

	let { children } = $props();

	onMount(() => {
		// BUG: this doesn't work unless reload (navigating doesn't activate this again)
		if (authState.token !== "") {
			goto("/account");
		}
	});
</script>

{@render children()}
