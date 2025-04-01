<script lang="ts">
  export let isVisible: boolean = true;
  export let size: "sm" | "md" | "lg" = "md";
  export let color: string = "border-blue-500";
  export let thickness: "thin" | "regular" | "thick" = "regular";
  export let speed: "slow" | "normal" | "fast" = "normal";

  const sizeMap = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  const thicknessMap = {
    thin: "border",
    regular: "border-2",
    thick: "border-4",
  };

  const speedMap = {
    slow: "animate-[spin_2s_linear_infinite]",
    normal: "animate-[spin_1s_linear_infinite]",
    fast: "animate-[spin_0.5s_linear_infinite]",
  };
</script>

{#if isVisible}
  <div class="flex items-center justify-center">
    <div
      class={`
        rounded-full
        ${sizeMap[size]}
        ${thicknessMap[thickness]}
        ${speedMap[speed]}
        border-t-transparent
        border-b-transparent
        ${color}
      `}
    ></div>
  </div>
{/if}
