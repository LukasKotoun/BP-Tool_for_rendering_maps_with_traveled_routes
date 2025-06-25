/**
 * Synchronizes loaded JSON data with the reference structure
 * Fills missing categories, subcategories, and properties with defaults
 * Removes categories/subcategories that don't exist in reference
 * Preserves existing values where they match the structure
 * Handles both 1-level and 2-level nested structures
 */
export function syncStoredMapElements(loadedData, referenceStructure) {
  const result = {};
  for (const [categoryKey, categoryValue] of Object.entries(referenceStructure)) {
    
    // Check if this is a direct property
    if (categoryValue.hasOwnProperty('plot')) {
      // 1-level structure: category -> properties
      result[categoryKey] = { ...categoryValue as object};
      
      // Override with loaded values if they exist
      if (loadedData?.[categoryKey] && typeof loadedData[categoryKey] === 'object') {
        const loadedItem = loadedData[categoryKey];
        
        // Preserve properties that exist in the reference structure
        for (const [propKey] of Object.entries(categoryValue)) {
          if (loadedItem.hasOwnProperty(propKey)) {
            result[categoryKey][propKey] = loadedItem[propKey];
          }
        }
      }
    } else {
      // 2-level structure: category -> subcategory -> properties
      result[categoryKey] = {};
      for (const [subKey, subValue] of Object.entries(categoryValue)) {
        // Start with defaults
        result[categoryKey][subKey] = { ...subValue };
        // Override with loaded values if they exist
        if (loadedData?.[categoryKey]?.[subKey] && typeof loadedData[categoryKey][subKey] === 'object') {
          const loadedSubItem = loadedData[categoryKey][subKey];
          
          // Preserve properties that exist in the reference structure
          for (const [propKey] of Object.entries(subValue)) {
            if (loadedSubItem.hasOwnProperty(propKey)) {
              result[categoryKey][subKey][propKey] = loadedSubItem[propKey];
            }
          }
        }
      }
    }
  }
  return result;
}
