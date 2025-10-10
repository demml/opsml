import type { PageLoad } from "./$types";

export const load: PageLoad = ({
  fetch,
  page,
  selectedSpace,
  selectedName,
}) => {
  // You can now use page, selectedSpace, selectedName here
  return { fetch, page, selectedSpace, selectedName };
};
