#!/usr/bin/env python3
"""
Investigate MCP types to understand proper notification options configuration
"""

import mcp.types as types

def investigate_notification_types():
    """Investigate available notification-related types in MCP"""
    print("🔍 Investigating MCP notification types...")
    
    notification_attrs = [attr for attr in dir(types) if 'notification' in attr.lower()]
    capability_attrs = [attr for attr in dir(types) if 'capability' in attr.lower()]
    
    print(f"\n📋 Notification-related types ({len(notification_attrs)}):")
    for attr in notification_attrs:
        print(f"  - {attr}")
    
    print(f"\n🔧 Capability-related types ({len(capability_attrs)}):")
    for attr in capability_attrs:
        print(f"  - {attr}")
    
    print(f"\n🔍 Investigating specific types...")
    
    if hasattr(types, 'ServerNotification'):
        server_notif = types.ServerNotification
        print(f"ServerNotification: {server_notif}")
        if hasattr(server_notif, '__annotations__'):
            print(f"  Annotations: {server_notif.__annotations__}")
    
    if hasattr(types, 'ToolsCapability'):
        tools_cap = types.ToolsCapability
        print(f"ToolsCapability: {tools_cap}")
        if hasattr(tools_cap, '__annotations__'):
            print(f"  Annotations: {tools_cap.__annotations__}")
    
    print(f"\n🧪 Testing type instantiation...")
    
    try:
        if hasattr(types, 'ToolsCapability'):
            tools_capability = types.ToolsCapability(listChanged=True)
            print(f"✅ ToolsCapability created: {tools_capability}")
    except Exception as e:
        print(f"❌ ToolsCapability creation failed: {e}")
    
    try:
        if hasattr(types, 'ServerNotification'):
            server_notification = types.ServerNotification()
            print(f"✅ ServerNotification created: {server_notification}")
    except Exception as e:
        print(f"❌ ServerNotification creation failed: {e}")

if __name__ == "__main__":
    investigate_notification_types()
