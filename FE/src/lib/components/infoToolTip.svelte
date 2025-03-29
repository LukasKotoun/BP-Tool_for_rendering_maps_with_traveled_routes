<script lang="ts">
    export let text: string = "Tooltip text";
    export let position: "top" | "right" | "bottom" | "left" = "top";
    export let size: "sm" | "md" | "lg" = "md";
    export let borderColor: string = "border-gray-600";
    const positions = {
      top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
      right: "left-full top-1/2 -translate-y-1/2 ml-2",
      bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
      left: "right-full top-1/2 -translate-y-1/2 mr-2"
    };
    
    const sizes = {
      sm: "w-4 h-4 text-xs border",
      md: "w-5 h-5 text-sm border-2",
      lg: "w-6 h-6 text-md border-2"
    };
    let displayTooltip = false;
  </script>
  
  <div class="relative inline-flex items-center justify-center" 
        role="tooltip"
      on:mouseenter={() => displayTooltip = true}
      on:mouseleave={() => displayTooltip = false}
      on:focus={() => displayTooltip = true}
      on:blur={() => displayTooltip = false}>
      
    <div class={`flex items-center justify-center rounded-full cursor-help ${borderColor} ${sizes[size]}`}>
      ?
    </div>
    {#if displayTooltip}
      <div class={`absolute z-10 ${positions[position]} bg-gray-800 text-white rounded px-3 py-2 text-sm shadow-lg max-w-xs pointer-events-none`}>
        {text}
      </div>
    {/if}
  </div>