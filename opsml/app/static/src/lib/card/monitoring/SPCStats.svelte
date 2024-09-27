<script lang="ts">

    import { type FeatureDriftProfile } from "$lib/scripts/types";
  
    export let feature_profile: FeatureDriftProfile;

  </script>
  
    <table class="table-compact table-cell-fit table-hover text-xs text-center min-w-full">
      <thead class="bg-primary-200 sticky top-0">
        <tr>
          <th class="text-sm text-center py-2">Zone</th>
          <th class="text-sm text-center py-2">Lower</th>
          <th class="text-sm text-center py-2">Upper</th>
        </tr>
      </thead>
      <tbody>
          <tr class="even:bg-gray-100">
            <td class="text-sm">Center</td>
            <td class="text-sm">{feature_profile.center}</td>
            <td class="text-sm">{feature_profile.center}</td>
          </tr>
          <tr class="even:bg-gray-100">
            <td class="text-sm">Zone 1</td>
            <td class="text-sm">{feature_profile.one_lcl}</td>
            <td class="text-sm">{feature_profile.one_ucl}</td>
          </tr>
          <tr class="even:bg-gray-100">
            <td class="text-sm">Zone 2</td>
            <td class="text-sm">{feature_profile.two_lcl}</td>
            <td class="text-sm">{feature_profile.two_ucl}</td>
          </tr>
          <tr class="even:bg-gray-100">
            <td class="text-sm">Zone 3</td>
            <td class="text-sm">{feature_profile.three_lcl}</td>
            <td class="text-sm">{feature_profile.three_ucl}</td>
          </tr>
      </tbody>
    </table>

  