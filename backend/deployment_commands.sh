#!/bin/bash

# DeFindex Strategy Contract Deployment Script
# Author: Generated for deploying all 5 DeFindex strategies to Stellar Testnet

echo "🌟 DeFindex Strategy Contract Deployment Script"
echo "================================================"

# Configuration
SECRET_KEY="SCXHJJVT7FGFRJ347GSB4LXRJAJKEPZN2EGGGGCWCWMBXMARQYDHAHIA"
NETWORK="testnet"
BASE_WASM_PATH="/home/ubuntu/blend-pools/backend/defindex/apps/contracts/target/wasm32v1-none/release"

# Check if soroban CLI is available
if ! command -v soroban &> /dev/null; then
    echo "❌ soroban CLI not found. Please install soroban CLI first."
    exit 1
fi

echo "✅ Soroban CLI found: $(soroban --version)"
echo "🔐 Using deployer account: ${SECRET_KEY:0:10}...${SECRET_KEY: -10}"
echo "🌍 Network: $NETWORK"
echo ""

# Strategy configurations
declare -A STRATEGIES=(
    ["HODL"]="hodl_strategy.wasm"
    ["BLEND"]="blend_strategy.wasm"
    ["SOROSWAP"]="soroswap_strategy.wasm"
    ["XYCLOANS"]="xycloans_adapter.wasm"
    ["FIXED_APR"]="fixed_apr_strategy.wasm"
)

# Log file for deployment results
LOG_FILE="deployment_results_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging results to: $LOG_FILE"

# Deploy each strategy
for strategy_name in "${!STRATEGIES[@]}"; do
    wasm_file="${STRATEGIES[$strategy_name]}"
    wasm_path="$BASE_WASM_PATH/$wasm_file"

    echo "🚀 Deploying $strategy_name strategy..."
    echo "   📦 WASM: $wasm_file"
    echo "   📍 Path: $wasm_path"

    if [[ -f "$wasm_path" ]]; then
        size=$(stat -c%s "$wasm_path")
        echo "   📊 Size: $size bytes"

        # Deploy contract
        echo "   🔧 Installing contract..."

        # Command to deploy the contract
        deploy_output=$(soroban contract install \
            --wasm "$wasm_path" \
            --network "$NETWORK" \
            --source-account "$SECRET_KEY" \
            2>&1)

        deploy_result=$?

        if [[ $deploy_result -eq 0 ]]; then
            echo "   ✅ $strategy_name deployment successful!"

            # Try to extract contract ID from output
            contract_id=$(echo "$deploy_output" | grep -o 'Contract ID: [a-zA-Z0-9]*' | cut -d' ' -f3)

            if [[ -n "$contract_id" ]]; then
                echo "   🎯 Contract ID: $contract_id"
                echo "   🔗 Explorer: https://stellar.expert/explorer/testnet/contract/$contract_id"
            else
                echo "   ⚠️  Contract deployment succeeded but couldn't extract contract ID"
                echo "   📋 Output: $deploy_output"
            fi
        else
            echo "   ❌ $strategy_name deployment failed!"
            echo "   📋 Error: $deploy_output"
        fi

        echo "   📝 Result logged to $LOG_FILE"
        echo "$deploy_output" >> "$LOG_FILE"

    else
        echo "   ❌ WASM file not found: $wasm_path"
    fi

    echo ""
    echo "---"
    echo ""
done

echo "🎉 Deployment script completed!"
echo "📄 Full logs available in: $LOG_FILE"
echo ""
echo "📊 Summary:"
echo "   Total strategies attempted: ${#STRATEGIES[@]}"
echo "   Check logs above for individual results"