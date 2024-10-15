import { apiHandler } from "$lib/scripts/apiHandler";
import {
  CommonPaths,
  type FileView,
  RegistryName,
  SaveName,
} from "$lib/scripts/types";
export async function getDataProfile(
  repository,
  name,
  version
): Promise<FileView> {
  const filePath: string = `opsml-root:/${RegistryName.Data}/${repository}/${name}/${version}/${SaveName.DataProfile}`;

  const viewData = await apiHandler.get(
    `${CommonPaths.FILES_VIEW}?${new URLSearchParams({
      path: filePath,
    }).toString()}`
  );

  const view = (await viewData.json()) as FileView;

  return view;
}
