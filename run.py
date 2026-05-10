import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.main import socketio, app

if __name__ == "__main__":
    print("=" * 50)
    print("   🌌 超级穿越模拟器 v1.0")
    print("   AI驱动的沉浸式角色扮演世界")
    print("=" * 50)
    print(f"\n   打开浏览器访问: http://localhost:5000\n")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
