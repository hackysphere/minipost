<script lang="ts">
	import { page } from "$app/state";
</script>

<h1>{page.status}</h1>
<p>{page.error?.message}</p>
{#if page.status === 500}
	<p><i>This might not actually be a bug, check your internet connection and see if reloading the page fixes this</i></p>
{/if}
