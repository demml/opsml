export const DEV_MOCK_COOKIE = "opsml_ui_dev_mock";
export const DEV_MOCK_STORAGE_KEY = "opsml-ui-dev-mock";

export function parseDevMockValue(value: string | undefined): boolean {
  return value === "true";
}
