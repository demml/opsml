import { afterEach, afterAll, vi, beforeAll, it } from "vitest";

import { server } from "./server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => {
  vi.restoreAllMocks();
  server.close();
});

import { render } from "@testing-library/svelte";

import Homepage from "../lib/Homepage.svelte";
import Card from "../lib/Card.svelte";
import ModelPage from "../routes/opsml/model/+page.svelte";
import ModelCardPage from "../routes/opsml/model/card/home/+page.svelte";
import ModelCardFiles from "../routes/opsml/model/card/files/+page.svelte";
import ModelCardMetadata from "../routes/opsml/model/card/metadata/+page.svelte";
import Versions from "../routes/opsml/model/card/versions/+page.svelte";
import type { RecentCards, CardJson } from "$lib/scripts/homepage";

import { type Files } from "$lib/scripts/types";
import { calculateTimeBetween } from "$lib/scripts/utils";
import { sampleCard, sampleModelMetadata, user } from "./constants";
import { ModelPageStore } from "$routes/store";

const cards: CardJson[] = [
  {
    date: "2021-09-01T00:00:00Z",
    app_env: "test",
    uid: "test",
    repository: "test",
    contact: "test",
    name: "test",
    version: "0.1.0",
    timestamp: 1711563309,
    tags: new Map(),
  },
];

const recentCards: RecentCards = {
  modelcards: cards,
  datacards: cards,
  runcards: cards,
};

it("render homepage", () => {
  render(Card, {
    hoverColor: "blue",
    repository: "test",
    name: "test",
    version: "0.1.0",
    timestamp: 1711563309,
    svgClass: "test",
    registry: "model",
  });
});

it("render span", () => {
  render(Homepage, { cards: recentCards });
});

it("render model page", () => {
  ModelPageStore.update((store) => {
    store.selectedRepo = "test";
    store.registryStats = { nbr_names: 1, nbr_versions: 1, nbr_repos: 1 };
    store.registryPage = { page: ["test", "test", 10, 120, 110, 10] };
    return store;
  });

  const data = {
    args: {
      repos: ["test"],
      searchTerm: undefined,
      selectedRepo: "test",
      registry: "test",
      registryStats: { nbr_names: 1, nbr_versions: 1, nbr_repos: 1 },
      registryPage: { page: ["test", "test", 10, 120, 110, 10] },
    },
  };
  render(ModelPage, { data });
});

it("render opsml/model/card/files", () => {
  const files: Files = {
    mtime: 1711563309,
    files: [
      {
        name: "test",
        size: 10,
        type: "test",
        created: 1711563309,
        islink: false,
        mode: 10,
        uid: 10,
        gid: 10,
        mtime: 1711563309,
        ino: 10,
        nlink: 10,
        uri: "test",
        suffix: ".md",
      },
    ],
  };
  const modifiedAt = calculateTimeBetween(files.mtime);
  const basePath = "test";

  const data = {
    repository: "test",
    registry: "test",
    name: "test",
    version: "test",
    displayPath: ["test"],
    subdir: "test",
    prevPath: "test",
    files,
    modifiedAt,
    basePath,
  };

  render(ModelCardFiles, { data });
});

it("render opsml/model/card/metadata", () => {
  const data = {
    metadata: {
      repository: "test",
      registry: "test",
      name: "test",
      metadata: {
        model_name: "test",
        model_class: "test",
        model_type: "test",
        model_interface: "test",
        model_uri: "test",
        model_version: "test",
        model_repository: "test",
        opsml_version: "1.0.0",
        data_schema: {
          data_type: "test",
          input_features: "test",
          ouput_features: "test",
          onnx_input_features: "test",
          onnx_output_features: "test",
          onnx_data_type: "test",
          onnx_version: "test",
        },
      },
    },
  };
  render(ModelCardMetadata, { data });
});

it("render opsml/model/card/versions", () => {
  const data = {
    nbr_cards: 10,

    name: "test",
    repository: "test",
    registry: "test",
    cards: {
      cards: [
        {
          date: "2021-09-01T00:00:00Z",
          uid: "test",
          repository: "test",
          contact: "test",
          name: "test",
          version: "0.1.0",
          timestamp: 1711563309,
          tags: new Map(),
          datacard_uid: "test",
          runcard_uid: "test",
        },
      ],
    },
  };
  render(Versions, { data });
});

it("render ModelCardPage", () => {
  const data = {
    hasReadme: true,
    readme: "test",
    card: sampleCard,
    metadata: sampleModelMetadata,
    uid: "test",
    registry: "model",
  };
  render(ModelCardPage, { data });
});
