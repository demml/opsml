import { render } from "@testing-library/svelte";
import { afterAll, afterEach, beforeAll, it } from "vitest";
import ModelCardPage from "../routes/opsml/model/card/+page.svelte";
import { server } from "./server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("render opsml/model/card", () => {
  const tags = new Map();
  tags.set("test", "test");

  const data = {
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
    hasReadme: true,
    card: {
      date: "test",
      uid: "test",
      repository: "test",
      contact: "test",
      name: "test",
      version: "test",
      timestamp: 1711563309,
      tags,
      datacard_uid: "test",
      runcard_uid: "test",
    },
  };

  render(ModelCardPage, { data });
});
