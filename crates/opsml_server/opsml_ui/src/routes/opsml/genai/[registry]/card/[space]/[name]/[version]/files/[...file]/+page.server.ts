import type { PageServerLoad } from "./$types";
import { loadFileTree } from "$lib/components/files/fileTreeLoader";

export const load: PageServerLoad = async (args) => {
  return await loadFileTree(args);
};
