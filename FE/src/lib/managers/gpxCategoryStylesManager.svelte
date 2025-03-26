<script lang="ts">
    import { gpxFiles, gpxStyles, gpxFileGroups} from '$lib/stores/mapStore';
    import { createUniqueName } from '$lib/utils/gpxFilesUtils';


    // State for new group input
    let newGroupName = '';

    let selectedFiles: string[] = []; // Tracked file names for the current group

    function addNewGroup() {
        console.log($gpxFileGroups)
        let groupName = newGroupName.trim();
        
        if (!groupName) {
            groupName = 'Nepojmenovaná skupina';
        }

        if ($gpxStyles.group[groupName]) {
            groupName = createUniqueName(Object.keys($gpxStyles.group), groupName);
        }

        $gpxStyles = {...$gpxStyles, group: {...$gpxStyles.group, [groupName]: {}}};
        $gpxFileGroups = {...$gpxFileGroups, [groupName]: []};
        newGroupName = '';
        console.log()
    }
    
    function getUngrupedFiles(): string[]{
        const groupedFiles = Object.values($gpxFileGroups).flat();
        return $gpxFiles
            .filter(gpxFile => 
                !groupedFiles.includes(gpxFile.file.name)
            )
            .map(gpxFile => gpxFile.file.name);
    }

    // Function to remove a group
    function removeGroup(groupName: string) {
        console.log($gpxStyles)
        // Remove from styles
        gpxStyles.update(styles => {
            const { [groupName]: removedGroup, ...remainingGroups } = styles.group;
            return {
                ...styles,
                group: remainingGroups
            };
        });

        // Remove from file groups mapping
        gpxFileGroups.update(fileGroups => {
            const { [groupName]: removedFileGroup, ...remainingFileGroups } = fileGroups;
            return remainingFileGroups;
        });
    }

    // Function to add or update files in a group
    function updateGroupFiles(groupName: string) {
        // Validate group and files
        if (!groupName || selectedFiles.length === 0) {
            return;
        }

        // Remove files from any existing groups
        gpxFileGroups.update(fileGroups => {
            const updatedFileGroups = { ...fileGroups };

            // First, remove selected files from all groups
            Object.keys(updatedFileGroups).forEach(group => {
                updatedFileGroups[group] = updatedFileGroups[group].filter(
                    fileName => !selectedFiles.includes(fileName)
                );
            });

            // Then add files to the selected group
            updatedFileGroups[groupName] = [
                ...(updatedFileGroups[groupName] || []),
                ...selectedFiles
            ];

            return updatedFileGroups;
        });

        // Clear selection
        selectedFiles = [];
    }
    
    function checkGroupMembership(fileName: string): boolean {
        for (const group in $gpxFileGroups) {
            if ($gpxFileGroups[group].includes(fileName)) {
                return true;
            }
        }
        return false
    }
    // Function to remove a file from a group
    function removeFileFromGroup(groupName: string, fileName: string) {
        gpxFileGroups.update(fileGroups => {
            const updatedFileGroups = { ...fileGroups };
            
            // Remove the specific file from the group
            updatedFileGroups[groupName] = 
                updatedFileGroups[groupName].filter(file => file !== fileName);

            return updatedFileGroups;
        });
    }
</script>

<div class="p-4 space-y-4">
    <div class="bg-gray-100 p-4 rounded-lg">
        <h2 class="text-xl font-bold mb-4">Nezařazené</h2>
        <div class="bg-white p-3 rounded shadow mb-2 flex flex-col">
            <!-- Existing Group Files -->
            
                <div class="mt-2">
                     {#if getUngrupedFiles().length > 0}
                    <div class="space-y-1">
                        {#each getUngrupedFiles() as fileName}
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
                on:click={addNewGroup} 
                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
                Přidat skupinu
            </button>
        </div>
    </div>

    <!-- Group Management Section -->
    <div class="bg-gray-100 p-4 rounded-lg">
        <h2 class="text-xl font-bold mb-4">Group Management</h2>
        
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
             
               

                <!-- File Selection for Group -->
                <div class="mt-2">
                    <select 
                        multiple 
                        bind:value={selectedFiles}
                        class="w-full p-2 border rounded mb-2"
                    >
                        {#each $gpxFiles as file}
                            {#if !checkGroupMembership(file.file.name)}
                            <option value={file.file.name}>
                                {file.file.name}
                            </option>
                            {/if}
                        {/each}
                    </select>
                    <button 
                        on:click={() => updateGroupFiles(groupName)}
                        class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 w-full"
                    >
                        Update Group Files
                    </button>
                </div>

                <!-- Existing Group Files -->
                {#if $gpxFileGroups[groupName] && $gpxFileGroups[groupName].length > 0}
                    <div class="mt-2">
                        <h3 class="font-medium mb-1">Files in Group:</h3>
                        <div class="space-y-1">
                            {#each $gpxFileGroups[groupName] as fileName}
                                <div class="flex justify-between items-center bg-gray-100 p-2 rounded">
                                    <span>{fileName}</span>
                                    <button 
                                        on:click={() => removeFileFromGroup(groupName, fileName)}
                                        class="text-red-500 hover:text-red-700"
                                    >
                                        Remove
                                    </button>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<style>
    /* Additional custom styles if needed */
</style>