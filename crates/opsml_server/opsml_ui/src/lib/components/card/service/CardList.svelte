<script lang="ts">

  import  CardButton from "./CardButton.svelte";
  import { type CardList } from "../card_interfaces/servicecard";

  let badgeColor = "#40328b";
  let iconColor = "#40328b";


  let {
    cardList,
  } = $props<{
    cardList: CardList;
  }>();

</script>
  
  {#each cardList.cards as card}
    <CardButton
      iconColor={iconColor} 
      badgeColor={badgeColor}
      name={card.name}
      space={card.space}
      version={card.version}
      registry={card.registry_type.toLowerCase()}
      alias={card.alias}
    />
  {/each}
    
 