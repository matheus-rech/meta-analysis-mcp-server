#!/usr/bin/env python3
"""
Investigate the correct MCP notification options structure
"""

import mcp.types as types
from mcp.server.lowlevel.server import Server

def investigate_notification_structure():
    """Investigate what notification_options should be"""
    print("🔍 Investigating MCP notification options structure...")
    
    server = Server("test")
    
    print(f"\n📋 Server get_capabilities method signature:")
    import inspect
    sig = inspect.signature(server.get_capabilities)
    print(f"  {sig}")
    
    print(f"\n🔍 Trying different notification option approaches...")
    
    class NotificationOptions:
        def __init__(self):
            self.tools_changed = True
            self.resources_changed = True
            self.prompts_changed = True
    
    try:
        notif_opts = NotificationOptions()
        print(f"✅ Custom NotificationOptions created: {notif_opts}")
        print(f"   tools_changed: {notif_opts.tools_changed}")
        
        caps = server.get_capabilities(
            notification_options=notif_opts,
            experimental_capabilities=None
        )
        print(f"✅ get_capabilities worked with custom NotificationOptions")
        print(f"   Capabilities: {caps}")
        
    except Exception as e:
        print(f"❌ Custom NotificationOptions failed: {e}")
    
    try:
        from types import SimpleNamespace
        simple_notif = SimpleNamespace(
            tools_changed=True,
            resources_changed=True,
            prompts_changed=True
        )
        
        caps = server.get_capabilities(
            notification_options=simple_notif,
            experimental_capabilities=None
        )
        print(f"✅ get_capabilities worked with SimpleNamespace")
        print(f"   Capabilities: {caps}")
        
    except Exception as e:
        print(f"❌ SimpleNamespace approach failed: {e}")

if __name__ == "__main__":
    investigate_notification_structure()
