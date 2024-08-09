// place files you want to import through the `$lib` alias in this folder.
import {
  getModalStore,
  type ModalStore,
  initializeStores,
} from "@skeletonlabs/skeleton";

export function loadModal(): ModalStore {
  try {
    const modalStore = getModalStore();
    return modalStore;
  } catch (error) {
    console.error(error);
    initializeStores();
    return getModalStore();
  }
}
