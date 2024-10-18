import { server } from "./server";
import { render } from "@testing-library/svelte";
import { exampleDataProfile } from "./constants";
import ProfilePage from "../routes/opsml/data/card/profile/+page.svelte";
import { storePopup } from "@skeletonlabs/skeleton";
import {
  computePosition,
  autoUpdate,
  offset,
  shift,
  flip,
  arrow,
} from "@floating-ui/dom";

storePopup.set({ computePosition, autoUpdate, offset, shift, flip, arrow });

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render Data Profile Page", async () => {
  let featureNames = Object.keys(exampleDataProfile.features);
  let profile = exampleDataProfile;

  let data = {
    profile: profile,
    featureNames: featureNames,
  };

  render(ProfilePage, { data });
});
