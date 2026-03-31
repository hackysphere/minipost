<script lang="ts">
	import type { Post } from "./openapi/types.gen";

	let { content }: { content: Post } = $props();
</script>

<div class="root-card">
	<p>{content.content}</p>
</div>

<style>
	.root-card {
		background-color: var(--ctp-mocha-surface0);
		padding: 5px;
		margin: 10px;
		border: solid 2px var(--ctp-mocha-overlay0);
		border-radius: 13px;
		word-break: break-word;
		white-space: preserve;
	}
</style>
