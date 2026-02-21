export const ssr = false;

import { redirect } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, params }) => {
  let url = `/opsml/genai/${params.registry}/card/${params.space}/${params.name}/${params.version}/monitoring/genai`;
  throw redirect(303, url);
};
