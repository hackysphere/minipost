<!-- FIXME:
<!-- TODO: this is not complete -->

<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { authState } from "$lib/AuthState.svelte";

	function logout() {
		authState.token = "";
		goto("/");
	}

	onMount(() => {
		if (authState.token === "") {
			goto("/auth", { replaceState: true });
		}
	});
</script>

<h1>account settings</h1>

<button onclick={logout} type="button">logout</button>
