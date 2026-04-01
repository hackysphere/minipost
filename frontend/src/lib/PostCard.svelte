<script lang="ts">
	import type { Post } from "./openapi/types.gen";

	let { content }: { content: Post } = $props();
</script>

<div class="root-card">
	<small>&Tab;{content.username}</small>
	<p>{content.content}</p>
</div>

<style>
	.root-card {
		background-color: var(--ctp-mocha-surface0);
		padding: 5px;
		margin: 10px;
		border: solid 2px var(--ctp-mocha-overlay0);
		border-radius: 13px;
	}
	.root-card p {
		margin-top: 5px;
		word-break: break-word;
		white-space: preserve;
	}
	.root-card small {
		color: var(--ctp-mocha-lavender);
	}
</style>
