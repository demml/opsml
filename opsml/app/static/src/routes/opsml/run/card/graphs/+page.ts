import { type Graph } from "$lib/scripts/types";
import { calculateTimeBetween, getRunGraphs } from "$lib/scripts/utils";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name = (url as URL).searchParams.get("name") as string | undefined;

  const repository = (url as URL).searchParams.get("repository") as
    | string
    | undefined;

  const version = (url as URL).searchParams.get("version") as
    | string
    | undefined;
  const graphs: Map<string, Graph> = await getRunGraphs(
    repository!,
    name!,
    version!
  );

  return {
    graphs,
  };
}
