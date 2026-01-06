#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Deployment Pipeline Checklist...${NC}"

# Go to website directory
cd website

# 1. Dependency Management
echo -e "\n${YELLOW}📦 [Step 1] Cleaning and Reinstalling Dependencies...${NC}"
rm -rf node_modules package-lock.json
npm install
echo -e "${GREEN}✅ Dependencies reinstalled.${NC}"

# 2. Linting
echo -e "\n${YELLOW}🔍 [Step 2] Running Lint Check...${NC}"
npm run lint
echo -e "${GREEN}✅ Lint check passed.${NC}"

# 3. Build Verification
echo -e "\n${YELLOW}🏗️ [Step 3] Verifying Build...${NC}"
npm run build
echo -e "${GREEN}✅ Build verification passed.${NC}"

# 4. Check for uncommitted changes
echo -e "\n${YELLOW}📝 [Step 4] Checking Git Status...${NC}"
cd ..
if [[ -n $(git status -s) ]]; then
  echo -e "${YELLOW}Detected changes:${NC}"
  git status -s
  
  echo -e "\n${YELLOW}Committing changes...${NC}"
  git add .
  git commit -m "chore(deploy): auto-fix dependencies and config for deployment"
  
  echo -e "\n${YELLOW}🚀 [Step 5] Pushing to Remote...${NC}"
  git push
  echo -e "${GREEN}✅ Successfully pushed to main.${NC}"
else
  echo -e "${GREEN}✨ No changes to commit. Repository is clean.${NC}"
  # Check if we are ahead of remote (need to push previous commits)
  if [[ -n $(git log origin/main..main) ]]; then
      echo -e "\n${YELLOW}🚀 [Step 5] Pushing local commits to Remote...${NC}"
      git push
      echo -e "${GREEN}✅ Successfully pushed to main.${NC}"
  else
      echo -e "${GREEN}✨ Everything is up to date.${NC}"
  fi
fi

echo -e "\n${GREEN}🎉 Deployment Pipeline Completed Successfully!${NC}"
