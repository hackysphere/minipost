<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { authState } from "$lib/AuthState.svelte";
	import type {
		BodyCreateAccount,
		BodyLogin,
		TokenEndpointReturn,
	} from "$lib/openapi/types.gen";

	let username = $state("");
	let password = $state("");
	let error = $state("");

	function login(signup: boolean = false) {
		if (!username) {
			error = "Username required";
			return;
		}
		if (!password) {
			error = "Password required";
			return;
		}

		let endpoint: string;
		let body: BodyLogin | BodyCreateAccount;
		if (signup) {
			endpoint = "/api/account/createaccount";
			body = {
				username: username,
				password: password,
			};
		} else {
			endpoint = "/api/token";
			body = {
				username: username,
				password: password,
				grant_type: "password",
			};
		}

		fetch(endpoint, {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
			},
			// manually setting type so that typescript doesn't freak out
			body: new URLSearchParams(body as Record<string, string>),
		})
			.then((res) => {
				switch (res.status) {
					case 200:
						res.json().then((res: TokenEndpointReturn) => {
							authState.token = res.access_token;
						});
						goto("/", { replaceState: true });
						break;
					case 401:
						error = "Invalid username/password";
						break;
					case 403:
						error = "Account disabled";
						break;
					case 409:
						error = "Username already taken";
						break;
					default:
						error = "Failed to login/signup";
						break;
				}
			})
			.catch(() => {
				error = "Failed to login/signup, server may be offline";
			});
		return;
	}

	onMount(() => {
		if (authState.token !== "") {
			goto("/account", { replaceState: true });
		}
	});
</script>

<h1>login</h1>

<div>
	<form>
		<input
			name="username"
			bind:value={username}
			placeholder="username"
			required
		>
		<input
			name="password"
			bind:value={password}
			placeholder="password"
			type="password"
			required
		>
		<button class="login" type="submit" onclick={() => login(false)}>
			login
		</button>
		<button class="signup" type="button" onclick={() => login(true)}>
			signup
		</button>
	</form>
	<p class="error">{error}</p>
</div>

<style>
	input {
		font-family: Inter, sans-serif;
		background-color: var(--ctp-mocha-surface1);
		color: var(--ctp-mocha-text);
		width: 100%;
		resize: none;
		border: none;
		padding: 10px;
		margin-bottom: 5px;
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
		background-color: var(--ctp-mocha-surface2);
		color: var(--ctp-mocha-text);
	}
	.login {
		background-color: var(--ctp-mocha-green);
		color: var(--ctp-mocha-base);
	}
	.signup {
		background-color: var(--ctp-mocha-blue);
		color: var(--ctp-mocha-base);
	}
	.error {
		color: var(--ctp-mocha-maroon);
	}
</style>
