<script lang="ts">
	import type { Post } from "./openapi/types.gen";

	let { content }: { content: Post } = $props();
</script>

<div class="root-card">
	<a class="username" href={`/user/${content.username}`}>{content.username}</a>
	<p>{content.content}</p>
	<a class="uuid" href={`/post/${content.uuid}`}>{content.uuid}</a>
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
	.root-card .username {
		color: var(--ctp-mocha-lavender);
		font-size: 0.85em;
		margin-left: 2em;
	}
	.root-card .username:hover {
		color: var(--ctp-mocha-mauve);
	}
	.root-card .uuid {
		font-size: 0.7em;
	}
</style>
