<script lang="ts">
	import { goto, invalidateAll } from "$app/navigation";
	import type { Post, PostBase } from "./openapi/types.gen";

	let {
		content,
		reply = false,
		basecontent = false,
	}: {
		content: Post | PostBase;
		reply?: boolean;
		basecontent?: boolean;
	} = $props();
	let posted_on_utc = $derived(new Date(content.posted_on / 1000000)); // need to convert from nanoseconds to milliseconds

	function deleteContent() {
		if (reply) {
			fetch(`/api/replies/${content.uuid}`, { method: "DELETE" }).then(
				invalidateAll,
			);
		} else {
			fetch(`/api/posts/${content.uuid}`, { method: "DELETE" }).then(() => {
				if (basecontent) {
					goto("/");
				} else {
					invalidateAll();
				}
			});
		}
	}
</script>

<!-- TODO: make this whole thing clickable -->
<div class="post-card">
	<a class="username" href={`/user/${content.username}`}>{content.username}</a>
	<p>{content.content}</p>
	<div class="metadata">
		<span>{posted_on_utc.toLocaleString()}</span>
		{#if !reply}
			<a class="uuid" href={`/post/${content.uuid}`}>{content.uuid}</a>
		{/if}
		<button class="delete-button" type="button" onclick={deleteContent}>
			delete
		</button>
	</div>
</div>

<style>
	.post-card {
		background-color: var(--ctp-mocha-surface0);
		padding: 5px;
		margin: 10px;
		border: solid 2px var(--ctp-mocha-overlay0);
		border-radius: 13px;
	}
	.post-card p {
		margin-top: 5px;
		word-break: break-word;
		white-space: preserve;
	}

	.username {
		color: var(--ctp-mocha-lavender);
		font-size: 0.85em;
	}
	.username:hover {
		color: var(--ctp-mocha-mauve);
	}

	.metadata {
		font-size: 0.7em;
		display: flex;
		gap: 5px 2em; /* pixels because line spacing, em because text spacing on same line */
		flex-wrap: wrap;
		color: var(--ctp-mocha-subtext0);
		font-family: JetBrainsMono, monospace;
	}
	.uuid {
		word-break: break-all;
	}

	.delete-button {
		color: var(--ctp-mocha-red);
		margin-left: auto;
		border: none;
		background-color: var(--ctp-mocha-surface1);
		border-radius: 5px;
		transition-duration: 200ms;
	}
	.delete-button:hover {
		color: var(--ctp-mocha-crust);
		background-color: var(--ctp-mocha-red);
	}
</style>
