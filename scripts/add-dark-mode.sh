#!/bin/bash

# Script to add dark mode classes to React/Next.js files
# Usage: ./scripts/add-dark-mode.sh

echo "Adding dark mode support to pages..."

# Define the files to update
FILES=(
  "frontend/src/app/contact/page.tsx"
  "frontend/src/app/about/page.tsx"
  "frontend/src/app/pricing/page.tsx"
  "frontend/src/app/features/page.tsx"
  "frontend/src/app/jobs/[id]/apply/page.tsx"
  "frontend/src/app/profile/edit/page.tsx"
)

# Backup files first
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    cp "$file" "$file.backup"
    echo "Backed up: $file"
  fi
done

# Apply dark mode transformations
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Processing: $file"
    
    # Background colors
    sed -i '' 's/bg-gray-50"/bg-gray-50 dark:bg-gray-900"/g' "$file"
    sed -i '' 's/bg-white"/bg-white dark:bg-gray-800"/g' "$file"
    sed -i '' 's/bg-blue-50"/bg-blue-50 dark:bg-blue-900\/20"/g' "$file"
    
    # Text colors
    sed -i '' 's/text-gray-900"/text-gray-900 dark:text-white"/g' "$file"
    sed -i '' 's/text-gray-600"/text-gray-600 dark:text-gray-300"/g' "$file"
    sed-i '' 's/text-gray-700"/text-gray-700 dark:text-gray-200"/g' "$file"
    
    # Borders
    sed -i '' 's/border-gray-200"/border-gray-200 dark:border-gray-700"/g' "$file"
    sed -i '' 's/border-gray-300"/border-gray-300 dark:border-gray-600"/g' "$file"
    
    echo "✓ Updated: $file"
  fi
done

echo "Done! Dark mode classes added."
echo "Note: Review the changes and test thoroughly before committing."
