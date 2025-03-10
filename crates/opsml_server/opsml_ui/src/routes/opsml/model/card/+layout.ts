export const prerender = true;
export const ssr = false;
import { opsmlClient } from "$lib/components/api/client.svelte";
import { RegistryType } from "$lib/utils";

// @ts-ignore
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ url }) => {
  await opsmlClient.validateAuth(true);

  const name = (url as URL).searchParams.get("name") as string | undefined;
  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;
  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const uid = (url as URL).searchParams.get("uid") as string | undefined;
  const registry = RegistryType.Model;

  const metadata: ModelMetadata = await getModelMetadata(
    name!,
    repository!,
    uid,
    version
  );

  return {};
};
