
export function createUniqueFileName(files: File[], originalFile: File): File {
    const extension = originalFile.name.split('.').pop();
    const baseName = originalFile.name.replace(`.${extension}`, '');
    
    let uniqueName = originalFile.name;
    let counter = 1;
    
    while (files.some(f => f.name === uniqueName)) {
      uniqueName = `${baseName}_${counter}.${extension}`;
      counter++;
    }
  
    // Create a new File with the unique name
    return new File([originalFile], uniqueName, {
      type: originalFile.type});
  }

  export function createUniqueName(names: string[], name: string): string {

    let uniqueName = name;
    let counter = 1;
    while (names.some(name => name === uniqueName)) {
      uniqueName = `${name}_${counter}`;
      counter++;
    }
  
    // Create a new File with the unique name
    return uniqueName;
  }

export function getUngrupedFiles(gpxFileGroups: GPXFileGroups, gpxFiles: File[]): string[]{
    const groupedFiles = Object.values(gpxFileGroups).flat();
    return gpxFiles
        .filter(gpxFile => 
            !groupedFiles.includes(gpxFile.name)
        )
        .map(gpxFile => gpxFile.name);
}

export function checkGroupMembership(gpxFileGroups: GPXFileGroups, fileName: string): boolean {
  for (const group in gpxFileGroups) {
      if (gpxFileGroups[group].includes(fileName)) {
          return true;
      }
  }
  return false
}
