#!/bin/bash
# Quick verification script for droid-executor-skill and droid-executor-mcp
# Usage: bash tests/quick_verify.sh

set -e

echo "=============================================="
echo "DROID EXECUTOR QUICK VERIFICATION"
echo "=============================================="

BRIDGE_PORT=53002
BRIDGE_URL="http://localhost:$BRIDGE_PORT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if port is open
check_port() {
    nc -z localhost $1 2>/dev/null
    return $?
}

# Test HTTP endpoint
test_endpoint() {
    local name=$1
    local payload=$2
    local expected_status=$3
    
    echo -n "Testing: $name... "
    
    response=$(curl -s -X POST "$BRIDGE_URL/execute" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null || echo '{"status":"connection_error"}')
    
    status=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "parse_error")
    
    if [ "$expected_status" = "" ] || [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}PASSED${NC} (status=$status)"
        return 0
    else
        echo -e "${RED}FAILED${NC} (expected=$expected_status, got=$status)"
        return 1
    fi
}

echo ""
echo "1. Checking directory structure..."
echo "----------------------------------------------"

# Check droid-executor-skill structure
echo -n "  droid-executor-skill/SKILL.md: "
[ -f "droid-executor-skill/SKILL.md" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo -n "  droid-executor-skill/LICENSE.txt: "
[ -f "droid-executor-skill/LICENSE.txt" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo -n "  droid-executor-skill/ecosystem.config.cjs: "
[ -f "droid-executor-skill/ecosystem.config.cjs" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo -n "  droid-executor-skill/scripts/bridge/: "
[ -d "droid-executor-skill/scripts/bridge" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo -n "  droid-executor-skill/references/: "
[ -d "droid-executor-skill/references" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

# Check droid-executor-mcp structure
echo -n "  droid-executor-mcp/mcp_server.py: "
[ -f "droid-executor-mcp/mcp_server.py" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo -n "  droid-executor-mcp/ecosystem.config.cjs: "
[ -f "droid-executor-mcp/ecosystem.config.cjs" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo -n "  droid-executor-mcp/bridges/: "
[ -d "droid-executor-mcp/bridges" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}MISSING${NC}"

echo ""
echo "2. Checking for removed files..."
echo "----------------------------------------------"

# Check that non-standard files are removed
echo -n "  No .factory in skill: "
[ ! -d "droid-executor-skill/.factory" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}EXISTS${NC}"

echo -n "  No .factory in mcp: "
[ ! -d "droid-executor-mcp/.factory" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}EXISTS${NC}"

echo -n "  No tests/ in mcp: "
[ ! -d "droid-executor-mcp/tests" ] && echo -e "${GREEN}OK${NC}" || echo -e "${RED}EXISTS${NC}"

echo ""
echo "3. Checking bridge connectivity..."
echo "----------------------------------------------"

echo -n "  Port $BRIDGE_PORT: "
if check_port $BRIDGE_PORT; then
    echo -e "${GREEN}OPEN${NC}"
    BRIDGE_RUNNING=true
else
    echo -e "${YELLOW}CLOSED${NC}"
    BRIDGE_RUNNING=false
fi

if [ "$BRIDGE_RUNNING" = true ]; then
    echo ""
    echo "4. Running input validation tests..."
    echo "----------------------------------------------"
    
    test_endpoint "Empty objective" '{"objective":""}' "error"
    test_endpoint "Whitespace objective" '{"objective":"   "}' "error"
    test_endpoint "Missing objective" '{}' "error"
    test_endpoint "Valid objective" '{"objective":"Test task","context":{"repo_root":"."}}' ""
else
    echo ""
    echo -e "${YELLOW}Skipping HTTP tests (bridge not running)${NC}"
    echo "To start the bridge:"
    echo "  cd droid-executor-skill && npx pm2 start ecosystem.config.cjs"
fi

echo ""
echo "5. Running property-based tests..."
echo "----------------------------------------------"

if [ -f "droid-executor-skill/.venv/bin/pytest" ]; then
    droid-executor-skill/.venv/bin/pytest droid-executor-skill/scripts/tests/ -v --tb=short 2>&1 | tail -20
else
    echo -e "${YELLOW}pytest not found in venv, trying system pytest...${NC}"
    python3 -m pytest droid-executor-skill/scripts/tests/ -v --tb=short 2>&1 | tail -20 || echo -e "${RED}pytest failed${NC}"
fi

echo ""
echo "=============================================="
echo "VERIFICATION COMPLETE"
echo "=============================================="
