<!-- FIXME:
<!-- TODO: this is not complete -->

<script lang="ts">
	import { authState } from "$lib/AuthState.svelte";
</script>

<h1>login</h1>

<input bind:value={authState.token} placeholder="token">

<br>

<a href="/auth/signup">signup</a>
