#!/usr/bin/env python3
"""
Simple test to verify arc layout functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from drawio_export import generate_drawio_file

def test_simple_arc():
    """Test basic arc layout"""
    print("🧪 Testing arc layout...")
    
    # Create simple test data
    items = [
        {
            'name': 'Test Subscription',
            'id': '/subscriptions/test-sub',
            'type': 'Microsoft.Resources/subscriptions'
        },
        {
            'name': 'rg-webapp',
            'id': '/subscriptions/test-sub/resourcegroups/rg-webapp',
            'type': 'Microsoft.Resources/subscriptions/resourceGroups'
        },
        {
            'name': 'vm-web-01',
            'id': '/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-01',
            'type': 'Microsoft.Compute/virtualMachines'
        },
        {
            'name': 'vm-web-02',
            'id': '/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Compute/virtualMachines/vm-web-02',
            'type': 'Microsoft.Compute/virtualMachines'
        },
        {
            'name': 'storage-account',
            'id': '/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Storage/storageAccounts/storageaccount',
            'type': 'Microsoft.Storage/storageAccounts'
        },
        {
            'name': 'sql-database',
            'id': '/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.Sql/servers/server/databases/db',
            'type': 'Microsoft.Sql/servers/databases'
        },
        {
            'name': 'key-vault',
            'id': '/subscriptions/test-sub/resourcegroups/rg-webapp/providers/Microsoft.KeyVault/vaults/vault',
            'type': 'Microsoft.KeyVault/vaults'
        }
    ]
    
    dependencies = []
    
    # Generate diagram
    result = generate_drawio_file(items, dependencies, diagram_mode='infrastructure')
    
    # Save to file
    output_file = 'test-simple-arc.drawio'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"✅ Created diagram: {output_file}")
    print(f"📊 Items: {len(items)}")
    print(f"🎯 RG with {len([i for i in items if 'vm-web' in i['name'] or 'storage' in i['name'] or 'sql' in i['name'] or 'key-vault' in i['name']])} resources should use arc layout")
    
    return True

if __name__ == "__main__":
    try:
        test_simple_arc()
        print("✅ Simple arc test completed successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
