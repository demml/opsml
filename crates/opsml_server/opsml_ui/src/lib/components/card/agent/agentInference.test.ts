import { describe, expect, it } from "vitest";
import { buildAuthHeaders, inferAgentContract, inferHealthEndpoint } from "./agentInference";
import type { AgentSpec } from "./types";
import type { DeploymentConfig } from "../card_interfaces/servicecard";

const baseSpec: AgentSpec = {
  name: "Support Agent",
  description: "Handles support requests",
  version: "1.0.0",
  capabilities: {
    streaming: true,
    pushNotifications: false,
    extendedAgentCard: false,
    extensions: [],
  },
  defaultInputModes: ["text"],
  defaultOutputModes: ["text"],
  supportedInterfaces: [
    {
      url: "https://agent.example.com/",
      protocolBinding: "HTTP+JSON",
      protocolVersion: "1.0",
      tenant: "default",
    },
    {
      url: "https://rpc.example.com",
      protocolBinding: "json-rpc",
      protocolVersion: "0.3.0",
      tenant: "default",
    },
  ],
  securityRequirements: [{ schemes: ["bearer"] }],
  securitySchemes: {
    bearer: {
      scheme: "bearer",
      bearerFormat: "JWT",
      description: "Bearer auth",
    },
    apiKey: {
      location: "header",
      name: "x-api-key",
    },
  },
  skills: [
    {
      format: "a2a",
      id: "chat",
      name: "Chat",
      description: "Chat skill",
      examples: ["hello"],
      inputModes: ["text"],
      outputModes: ["text"],
      tags: ["support"],
      securityRequirements: [{ schemes: ["bearer"] }],
    },
    {
      format: "standard",
      name: "ignored",
      description: "Not an a2a skill",
    },
  ],
};

describe("agentInference", () => {
  it("infers endpoints for each A2A skill/interface pair", () => {
    const contract = inferAgentContract(baseSpec);
    expect(contract.skills).toHaveLength(1);
    expect(contract.skills[0]?.endpoints).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          protocol: "http+json",
          path: "https://agent.example.com/message:send",
        }),
        expect.objectContaining({
          protocol: "jsonrpc",
          path: "https://rpc.example.com",
        }),
      ]),
    );
  });

  it("builds auth headers from bearer and api-key schemes", () => {
    expect(
      buildAuthHeaders(baseSpec.securitySchemes ?? {}, {
        bearer: "token",
        apiKey: "secret",
      }),
    ).toEqual({
      "Content-Type": "application/json",
      Authorization: "Bearer token",
      "x-api-key": "secret",
    });
  });

  it("derives healthcheck URLs from deployment config", () => {
    const urls = inferHealthEndpoint([
      {
        environment: "prod",
        urls: ["https://service.example.com/"],
        healthcheck: "readyz",
      },
    ] satisfies DeploymentConfig[]);
    expect(urls).toEqual(["https://service.example.com/readyz"]);
  });
});
