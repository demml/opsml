import type { RequestHandler } from './$types';
import { getFileTree } from '$lib/server/card/files/utils';
import { json } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ url, fetch }) => {
  const path = url.searchParams.get('path') ?? '';
  const tree = await getFileTree(fetch, path);
  return json(tree);
};
