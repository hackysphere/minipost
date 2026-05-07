<script lang="ts">
	type CallbackFunction = (postContent: string, postUserId: string) => void;
	let {
		callback,
		error: errorContent,
	}: { callback: CallbackFunction; error?: string } = $props();

	let postUserId: string = $state("");
	let postContent: string = $state("");

	function shortcutHandler(event: KeyboardEvent) {
		if (event.ctrlKey && event.key === "Enter") {
			callCallback();
		}
	}

	function callCallback() {
		if (postContent.trim() !== "" && postUserId.trim() !== "") {
			callback(postContent, postUserId);
		}
	}
</script>

<input
	placeholder="user id"
	bind:value={postUserId}
	onkeydown={shortcutHandler}
>
<textarea
	placeholder="enter your post..."
	bind:value={postContent}
	onkeydown={shortcutHandler}
></textarea>
<button type="submit" onclick={callCallback}>publish!</button>
<span style="color: var(--ctp-mocha-subtext0)">(ctrl+enter)</span>
{#if errorContent}
	<p class="error">{errorContent}</p>
{/if}

<style>
	textarea,
	input {
		font-family: Inter, sans-serif;
		background-color: var(--ctp-mocha-surface1);
		color: var(--ctp-mocha-text);
		width: 100%;
		resize: none;
		border: none;
		padding: 10px;
		border-radius: 5px;
		box-sizing: border-box; /* this stops the box from overflowing into parent's margin, without doing messy stuff with maths on width */
	}
	button {
		margin: 10px;
		margin-left: 0px;
		padding: 7px;
		font-size: 1.2rem;
		border-radius: 7px;
		border: none;
		background-color: var(--ctp-mocha-green);
		color: var(--ctp-mocha-base);
	}
	.error {
		color: var(--ctp-mocha-maroon);
	}
</style>
