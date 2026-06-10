<script lang="ts">
	import { onMount } from "svelte";
	import { goto, invalidateAll } from "$app/navigation";
	import { authState } from "$lib/AuthState.svelte";
	import type {
		BodyDeleteAccount,
		BodySetPassword,
		BodySetUsername,
	} from "$lib/openapi/types.gen";
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();

	let deleteAccountStage2 = $state(false);

	// could be better done... (without state)
	let newUsernameField = $state("");
	let newPasswordCurrentPasswordField = $state("");
	let newPasswordNewPasswordField = $state("");
	let newPasswordNewPasswordAgainField = $state("");
	let deleteAccountPasswordField = $state("");

	let changeUsernameError = $state("");
	let changePasswordError = $state("");
	let deleteAccountError = $state("");

	function logout() {
		goto("/auth/logout");
	}

	function changeUsername() {
		if (!newUsernameField.trim()) {
			changeUsernameError = "Username required";
			return;
		}

		const body: BodySetUsername = {
			new_username: newUsernameField.trim(),
		};
		fetch("/api/account/changeusername", {
			method: "POST",
			headers: {
				Authorization: `Bearer ${authState.token}`,
				"Content-Type": "application/x-www-form-urlencoded",
			},
			body: new URLSearchParams(body),
		})
			.then((res) => {
				switch (res.status) {
					case 200:
						newUsernameField = "";
						invalidateAll();
						break;
					case 401:
					case 403:
						logout();
						break;
					case 400:
						res
							.text()
							.then((err_response) => {
								changeUsernameError = JSON.parse(err_response).detail;
							})
							.catch(() => {
								changeUsernameError = "Server failed to parse username";
							});
						break;
					case 409:
						changeUsernameError = "Username already taken";
						break;
					default:
						changeUsernameError = "Failed to change username";
						break;
				}
			})
			.catch(() => {
				changeUsernameError =
					"Failed to change username, server might be offline";
			});
	}

	function changePassword() {
		if (!newPasswordCurrentPasswordField) {
			changePasswordError = "Current password required";
			return;
		}
		if (!newPasswordNewPasswordField) {
			changePasswordError = "New password required";
			return;
		}
		if (!newPasswordNewPasswordAgainField) {
			changePasswordError = "New password confirmation required";
			return;
		}
		if (newPasswordNewPasswordField !== newPasswordNewPasswordAgainField) {
			changePasswordError = "New passwords do not match";
			return;
		}

		const body: BodySetPassword = {
			old_password: newPasswordCurrentPasswordField,
			new_password: newPasswordNewPasswordField,
		};
		fetch("/api/account/changepassword", {
			method: "POST",
			headers: {
				Authorization: `Bearer ${authState.token}`,
				"Content-Type": "application/x-www-form-urlencoded",
			},
			body: new URLSearchParams(body),
		})
			.then((res) => {
				switch (res.status) {
					case 200:
					case 401:
						logout();
						break;
					case 403:
						// the user might also be disabled...
						changePasswordError = "Invalid current password";
						break;
					default:
						changePasswordError = "Failed to change password";
						break;
				}
			})
			.catch(() => {
				changePasswordError =
					"Failed to change password, server might be offline";
			});
	}

	function deleteAccount() {
		if (!deleteAccountPasswordField) {
			deleteAccountError = "Password required";
			return;
		}

		const body: BodyDeleteAccount = {
			password: deleteAccountPasswordField,
		};
		fetch("/api/account/deleteaccount", {
			method: "DELETE",
			headers: {
				Authorization: `Bearer ${authState.token}`,
				"Content-Type": "application/x-www-form-urlencoded",
			},
			body: new URLSearchParams(body),
		})
			.then((res) => {
				switch (res.status) {
					case 200:
					case 401:
						logout();
						break;
					case 403:
						// the user might also be disabled...
						deleteAccountError = "Invalid current password";
						break;
					default:
						deleteAccountError = "Failed to delete account";
						break;
				}
			})
			.catch(() => {
				deleteAccountError =
					"Failed to delete account, server might be offline";
			});
	}

	onMount(() => {
		if (authState.token === "") {
			goto("/auth", { replaceState: true });
		}
	});
</script>

{#if !deleteAccountStage2}
	<h1>account settings</h1>

	<div>
		<p class="userinfo">
			<b>{data.username}</b><br>
			<small
				>joined on
				<span class="monospaced"
					>{new Date(data.creation_ts / 1e6).toLocaleString()}</span
				><br>
				uuid <span class="monospaced">{data.user_id}</span><br>
				<a href={`/user/${authState.user_id}`}>go to profile</a></small
			>
		</p>
		<button class="logout" type="button" onclick={logout}>logout</button>
	</div>

	<hr>

	<h2>change username</h2>
	<form>
		<input
			name="username"
			placeholder="new username"
			bind:value={newUsernameField}
			required
		>
		<button type="submit" onclick={changeUsername}>change username</button>
		<span class="error">{changeUsernameError}</span>
	</form>

	<hr>

	<h2>change password</h2>
	<p>you will be logged out when your password is changed</p>
	<form>
		<input
			name="oldpassword"
			type="password"
			placeholder="current password"
			bind:value={newPasswordCurrentPasswordField}
			required
		>
		<input
			name="password"
			type="password"
			placeholder="new password"
			bind:value={newPasswordNewPasswordField}
			required
		>
		<input
			name="password"
			type="password"
			placeholder="repeat new password"
			bind:value={newPasswordNewPasswordAgainField}
			required
		>
		<button type="submit" onclick={changePassword}>change password</button>
		<span class="error">{changePasswordError}</span>
	</form>

	<hr>

	<button
		class="danger"
		type="button"
		onclick={() => (deleteAccountStage2 = true)}
	>
		delete account
	</button>
{:else}
	<div class="danger">
		<h1>account settings → delete account</h1>
		<h3>are you sure??</h3>
		<p>there's no going back!</p>
		<form>
			<input
				type="password"
				placeholder="password"
				bind:value={deleteAccountPasswordField}
				required
			>
			<button type="submit" onclick={deleteAccount}>
				really delete account!
			</button>
			<button
				class="safe"
				type="button"
				onclick={() => {
					deleteAccountStage2 = false;
					deleteAccountPasswordField = "";
				}}
			>
				go back
			</button>
		</form>
		<p class="error">{deleteAccountError}</p>
	</div>
{/if}

<style>
	hr {
		background-color: var(--ctp-mocha-surface0);
		border: none;
		height: 3px;
		border-radius: 10px;
	}
	input {
		font-family: var(--font-body);
		background-color: var(--ctp-mocha-surface1);
		color: var(--ctp-mocha-text);
		width: 100%;
		resize: none;
		border: none;
		padding: 10px;
		border-radius: 5px;
		box-sizing: border-box; /* this stops the box from overflowing into parent's margin, without doing messy stuff with maths on width */
	}
	button,
	.danger button.safe {
		font-family: var(--font-body);
		margin: 10px;
		margin-left: 0px;
		padding: 7px;
		font-size: 1.2rem;
		border-radius: 7px;
		border: none;
		background-color: var(--ctp-mocha-blue);
		color: var(--ctp-mocha-base);
	}
	.logout {
		background-color: var(--ctp-mocha-peach);
		color: var(--ctp-mocha-base);
	}
	.error,
	.danger {
		color: var(--ctp-mocha-maroon);
	}
	.danger button,
	.danger input,
	button.danger {
		color: var(--ctp-mocha-base);
		background-color: var(--ctp-mocha-maroon);
	}

	.userinfo {
		font-size: 1.2em;
	}

	.monospaced {
		font-family: var(--font-mono);
	}
</style>
