import { type RunGraph } from "$lib/scripts/types";
import { getRunGraphs } from "$lib/scripts/utils";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;

  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const graphs: Map<string, RunGraph> = await getRunGraphs(
    repository!,
    name!,
    version!
  );

  return {
    graphs,
  };
}
