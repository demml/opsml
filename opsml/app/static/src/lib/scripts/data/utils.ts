import { apiHandler } from "$lib/scripts/apiHandler";
import {
  CommonPaths,
  type FileView,
  RegistryName,
  SaveName,
} from "$lib/scripts/types";
import { type DataProfile } from "$lib/scripts/data/types";
export async function getDataProfile(
  repository,
  name,
  version
): Promise<DataProfile> {
  const filePath: string = `opsml-root:/${RegistryName.Data}/${repository}/${name}/v${version}/${SaveName.DataProfile}`;

  const viewData = await apiHandler.get(
    `${CommonPaths.FILES_VIEW}?${new URLSearchParams({
      path: filePath,
    }).toString()}`
  );

  const view = (await viewData.json()) as FileView;
  let content: string = view.content.content!;

  let profile: DataProfile = JSON.parse(content);

  return profile;
}
