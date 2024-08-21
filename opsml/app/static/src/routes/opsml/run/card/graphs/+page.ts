import { type Graph } from "$lib/scripts/types";
import { calculateTimeBetween, getRunGraphs } from "$lib/scripts/utils";

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  const name: string | null = (url as URL).searchParams.get("name");

  const repository: string | null = (url as URL).searchParams.get("repository");

  const version: string | null = (url as URL).searchParams.get("version");
  const graphs: Map<string, Graph> = await getRunGraphs(
    repository!,
    name!,
    version!
  );

  return {
    graphs,
  };
}
