import { server } from "./server";
import { render } from "@testing-library/svelte";
import { afterAll, afterEach, beforeAll, it } from "vitest";

import DataPage from "../routes/opsml/data/+page.svelte";
import DataCardPage from "../routes/opsml/data/card/+page.svelte";
import DataCardFiles from "../routes/opsml/data/card/files/+page.svelte";
import DataCardSplits from "../routes/opsml/data/card/splits/+page.svelte";
import DataVersionPage from "../routes/opsml/data/card/versions/+page.svelte";
import DataSqlPage from "../routes/opsml/data/card/sql/+page.svelte";

import { type Files } from "$lib/scripts/types";
import * as utils from "../lib/scripts/utils";
import {
  sampleCard,
  sampleDataMetadata,
  sampleFiles,
  sampleCards,
} from "./constants";
import { registry } from "chart.js";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render dataPage", async () => {
  const registryPage = await utils.setupRegistryPage("model");
  const data = {
    args: {
      repos: ["data"],
      searchTerm: undefined,
      selectedRepo: "data",
      registryStats: registryPage.registryStats,
      registryPage: registryPage.registryPage,
      registry: "data",
    },
  };

  render(DataPage, { data });
});

it("render DataCardPage", async () => {
  const data = {
    hasReadme: true,
    readme: "test",
    card: sampleCard,
    metadata: sampleDataMetadata,
    registry: "data",
  };

  render(DataCardPage, { data });
});

it("render DataCardFiles", async () => {
  const modifiedAt = utils.calculateTimeBetween(sampleFiles.mtime);
  const basePath = "test";

  const data = {
    repository: "test",
    registry: "test",
    name: "test",
    version: "test",
    displayPath: ["test"],
    subdir: "test",
    prevPath: "test",
    files: sampleFiles,
    modifiedAt,
    basePath,
  };

  render(DataCardFiles, { data });
});

it("render DataCardSplits", async () => {
  const data = {
    metadata: sampleDataMetadata,
  };

  render(DataCardSplits, { data });
});

it("render DataVersionPage", async () => {
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
  render(DataVersionPage, { data });
});

// sql
it("render sqlPage", async () => {
  const registryPage = await utils.setupRegistryPage("sql");
  const data = {
    metadata: sampleDataMetadata,
  };

  render(DataSqlPage, { data });
});
