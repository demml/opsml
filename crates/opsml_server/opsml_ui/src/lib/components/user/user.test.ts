import { describe, expect, it } from "vitest";
import { UserStore, getGroupPermissions, getPermissions } from "./user.svelte";

describe("user store helpers", () => {
  it("normalizes empty permission resources to all", () => {
    expect(getPermissions(["read:", "write:space-a"])).toEqual([
      ["read", "all"],
      ["write", "space-a"],
    ]);
    expect(getGroupPermissions(["admin:"])).toEqual([["admin", "all"]]);
  });

  it("updates and resets user state", () => {
    const store = new UserStore();
    store.updateUser("alice", ["read:space-a"], ["admin:"], ["space-a"]);
    expect(store.logged_in).toBe(true);
    expect(store.username).toBe("alice");
    expect(store.favorite_spaces).toEqual(["space-a"]);

    store.resetUser();
    expect(store.logged_in).toBe(false);
    expect(store.username).toBe("");
    expect(store.favorite_spaces).toEqual([]);
  });
});
