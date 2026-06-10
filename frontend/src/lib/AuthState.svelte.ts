import { browser } from "$app/env";

// if using SSR, this gets called twice:
// - once on page load from server
// - once for local hydration
// if user has JS disabled then account actions wouldn't work anyways
//
// structure taken from https://stackoverflow.com/a/79261081
export const authState = (() => {
	// this actually doesn't have to be in a changed object (since this isn't being modified directly as an import)
	// but there's no real reason to add that confusion into this yet
	const auth = $state({
		token: (() => {
			if (!browser) return "TOKENLOAD";
			return localStorage.getItem("jwt") ?? "";
		})(),
	});

	const user = $derived.by(() => {
		try {
			const jwt_payload = auth.token.split(".")[1];
			const payload = JSON.parse(atob(jwt_payload));

			return payload.sub;
		} catch {
			return "noid";
		}
	});

	return {
		get token() {
			return auth.token;
		},
		set token(value) {
			auth.token = value;
		},
		get user_id() {
			return user;
		},
	};
})();

// this is supposed to have a cleanup function, but it doesn't seem to get initialized more than once per session
// there are also no callbacks or timeouts to cleanup
// if memory leaks happen then this should be converted to a store (or even a Proxy ?)
if (browser) {
	$effect.root(() => {
		$effect(() => {
			localStorage.setItem("jwt", authState.token);
		});

		return () => {};
	});
}
