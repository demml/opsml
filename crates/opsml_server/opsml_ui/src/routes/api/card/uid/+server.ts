import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { getCardfromUid } from "$lib/server/card/utils";
import { RegistryType } from "$lib/utils";

/**
 * Server route to fetch card information by UID.
 * Client should provide the UID in the request.
 */
export const GET: RequestHandler = async ({ fetch, url }) => {
  let registry_type: RegistryType = url.searchParams.get(
    "registry_type"
  ) as RegistryType;
  let uid = url.searchParams.get("uid") || "";
  let response = await getCardfromUid(registry_type, uid, fetch);

  // Return card info to client for further handling
  return json(response);
};
