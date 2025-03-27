<script lang="ts">
    import { gpxFiles, gpxStyles, gpxFileGroups} from '$lib/stores/mapStore';
    import { gpxDefaultStyles } from '$lib/constants';
    import { createUniqueName, getUngrupedFiles, checkGroupMembership } from '$lib/utils/gpxFilesUtils';

    let newGroupName = '';
    let selectedFiles:{[groupName: string]: string[]} = {};
    for (const group in $gpxFileGroups) {
        selectedFiles[group] = [];
    }

    function createGroup() {
        let groupName = newGroupName.trim();
        
        if (!groupName) {
            groupName = 'Nepojmenovaná skupina';
        }

        if ($gpxStyles.group[groupName]) {
            groupName = createUniqueName(Object.keys($gpxStyles.group), groupName);
        }
        selectedFiles[groupName] = [];
        $gpxStyles = {...$gpxStyles, group: {...$gpxStyles.group, [groupName]: JSON.parse(JSON.stringify(gpxDefaultStyles))}};
        $gpxFileGroups = {...$gpxFileGroups, [groupName]: []};
        newGroupName = '';
    }

    function removeGroup(groupName: string) {
        //remove from styles
        const { [groupName]: removedGroup, ...remainingGroupsStyles } = $gpxStyles.group;
        $gpxStyles = {...$gpxStyles, group: remainingGroupsStyles};
        //remove from groups
        const { [groupName]: _, ...remainingGroupsGroups } = $gpxFileGroups;    
        $gpxFileGroups = {...remainingGroupsGroups};
    }

    function updateGroupFiles(groupName: string) {
        if (!groupName || !selectedFiles.hasOwnProperty(groupName) || selectedFiles[groupName].length === 0) {
            return;
        }
        $gpxFileGroups[groupName] = [...$gpxFileGroups[groupName], ...selectedFiles[groupName]];
        selectedFiles[groupName] = [];
    }
    

    // Function to remove a file from a group
    function removeFileFromGroup(groupName: string, fileName: string) {
        $gpxFileGroups[groupName] = $gpxFileGroups[groupName].filter(file => file !== fileName);
    }
</script>

<div class="p-4 space-y-4">
    <div class="bg-gray-100 p-4 rounded-lg">
        <h2 class="text-xl font-bold mb-4">Nezařazené</h2>
        <div class="bg-white p-3 rounded shadow mb-2 flex flex-col">
            <!-- Existing Group Files -->
            
                <div class="mt-2">
                     {#if getUngrupedFiles($gpxFileGroups, $gpxFiles).length > 0}
                    <div class="space-y-1">
                        {#each getUngrupedFiles($gpxFileGroups, $gpxFiles) as fileName}
                            <div class="flex justify-between items-center bg-gray-100 p-2 rounded">
                                <span>{fileName}</span>
                            </div>
                        {/each}
                    </div>
                    {:else}
                        <div class="space-y-1 p-4">
                            <p>Žádné nezařazené soubory </p>
                        </div>
                    {/if}
                </div>
           

        </div>
    </div>
    <div class="bg-gray-100 p-4 rounded-lg">
        <h2 class="text-xl font-bold mb-4">Vytvořit vlastní skupinu</h2>
        <div class="flex space-x-2 mb-4">
            <input 
                type="text" 
                bind:value={newGroupName} 
                placeholder="Název skupiny" 
                class="flex-grow p-2 border rounded"
            />
            <button 
                on:click={createGroup} 
                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
                Přidat skupinu
            </button>
        </div>
    </div>

    <!-- Group Management Section -->
    <div class="bg-gray-100 p-4 rounded-lg">
        <h2 class="text-xl font-bold mb-4">Vlastní skupiny</h2>
        
        {#each Object.entries($gpxFileGroups) as [groupName, files]}
            <div class="bg-white p-3 rounded shadow mb-2 flex flex-col">
              
                <div class="flex justify-between items-center mb-2">
                    <span class="font-semibold">{groupName}</span>
                    <button 
                        on:click={() => removeGroup(groupName)}
                        class="text-red-500 hover:text-red-700"
                    >
                        Odstranit skupinu
                    </button>
                </div>
             
                <div class="flex justify-between items-center mb-2">
                    
                    <select 
                        multiple 
                        bind:value={selectedFiles[groupName]}
                        class="w-full p-2 border rounded mr-4 h-20"
                    >
                        {#each $gpxFiles as file}
                            {#if !checkGroupMembership($gpxFileGroups, file.name)}
                            <option value={file.name}>
                                {file.name}
                            </option>
                            {/if}
                        {/each}
                    </select>
                    <button 
                        on:click={() => updateGroupFiles(groupName)}
                        class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                    >
                        Přidat vybrané soubory
                    </button>
                </div>

                <!-- Existing Group Files -->
                <div class="mt-2">
                    <h3 class="font-medium mb-1">Soubory ve skupině:</h3>
                    {#if $gpxFileGroups[groupName] && $gpxFileGroups[groupName].length > 0}
                        <div class="space-y-1">
                            {#each $gpxFileGroups[groupName] as fileName}
                                <div class="flex justify-between items-center bg-gray-100 p-2 rounded">
                                    <span>{fileName}</span>
                                    <button 
                                        on:click={() => removeFileFromGroup(groupName, fileName)}
                                        class="text-red-500 hover:text-red-700"
                                    >
                                        Odebrat
                                    </button>
                                </div>
                            {/each}
                        </div>
                        {:else}
                        <div class="space-y-1 p-4">
                            <p>Žádné soubory ve skupině</p>
                        </div>
                        {/if}
                    </div>
            </div>
        {/each}
    </div>
</div>

