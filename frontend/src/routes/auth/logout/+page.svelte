<script lang="ts">
	// this route exists to logout from 401/403 errors on the client
	// (for things like load functions)

	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { authState } from "$lib/AuthState.svelte";

	onMount(() => {
		authState.token = "";
		goto("/auth", { replaceState: true });
	});
</script>

<h1>logging out...</h1>
