export const ssr = false;

import { redirect } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ parent, params }) => {
  const { driftTypes } = await parent();

  // Redirect to the first available drift type
  const defaultDriftType = driftTypes[0];

  throw redirect(
    303,
    `/opsml/${params.registry}/card/${params.space}/${params.name}/${params.version}/monitoring/${defaultDriftType}`
  );
};
