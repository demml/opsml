import { CommonPaths, type securityQuestionResponse } from "$lib/scripts/types";
import { getSecurityQuestion } from "$lib/scripts/auth_routes";

export const ssr = false;

/** @type {import('./$types').PageLoad} */
export async function load({ fetch, params, url }) {
  let username: string | null = url.searchParams.get("username");
  let secretQuestion: securityQuestionResponse | null = null;

  if (username) {
    secretQuestion = await getSecurityQuestion(username);
  }

  return {
    username,
    secretQuestion,
  };
}
