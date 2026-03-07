<script lang="ts">
	let { content }: { content: string | number } = $props();
</script>

<div class="root-card">
	<p>{content}</p>
</div>

<style>
	.root-card {
		background-color: hsl(237deg, 16%, 23%);
		padding: 5px;
		margin: 10px;
		border: solid 2px hsl(231deg, 11%, 47%); 
		border-radius: 13px;
	}
</style>
