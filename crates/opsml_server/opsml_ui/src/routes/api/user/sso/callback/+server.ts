import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";
import { exchangeSsoCallbackCode } from "$lib/server/user/utils";
import {
  setTokenInCookies,
  setUsernameInCookies,
} from "$lib/server/auth/validateToken";

export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const { code, code_verifier } = await request.json();
  const loginResponse = await exchangeSsoCallbackCode(
    code,
    code_verifier,
    fetch
  );
  setTokenInCookies(cookies, loginResponse.jwt_token);
  setUsernameInCookies(cookies, loginResponse.username);

  // mask the token in the response after setting the cookie
  loginResponse.jwt_token = "*****";

  return json(loginResponse);
};
