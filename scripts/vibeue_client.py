"""Raw MCP JSON-RPC client for the in-editor VibeUE server on :8088.

Usage:
  python vibeue_client.py tools/list
  python vibeue_client.py call <tool_name> '<json_args>'
  python vibeue_client.py py <python_file>       # execute_python_code from file
"""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8088/mcp"
_session_id = None


def _post(payload, extra_headers=None):
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(BASE, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        sid = resp.headers.get("Mcp-Session-Id")
        body = resp.read().decode("utf-8", errors="replace")
    return sid, body


def _parse_sse(body):
    # concatenate data: lines into one JSON doc
    chunks = [ln[5:].strip() for ln in body.splitlines() if ln.startswith("data:")]
    if chunks:
        return json.loads("".join(chunks))
    return json.loads(body) if body.strip() else None


def init():
    global _session_id
    sid, _ = _post({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "claude-fallback", "version": "1.0"},
        },
    })
    _session_id = sid
    _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
          {"Mcp-Session-Id": _session_id} if _session_id else None)


def call(method, params=None, rid=2):
    hdr = {"Mcp-Session-Id": _session_id} if _session_id else None
    _, body = _post({"jsonrpc": "2.0", "id": rid, "method": method, "params": params or {}}, hdr)
    return _parse_sse(body)


def main():
    init()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tools/list"
    if cmd == "tools/list":
        res = call("tools/list")
        names = [t["name"] for t in res["result"]["tools"]]
        print("\n".join(names))
    elif cmd == "call":
        tool = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        res = call("tools/call", {"name": tool, "arguments": args})
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif cmd == "py":
        code = open(sys.argv[2], encoding="utf-8").read()
        res = call("tools/call", {"name": "execute_python_code", "arguments": {"code": code}})
        # unwrap text content for readability
        try:
            for c in res["result"]["content"]:
                if c.get("type") == "text":
                    print(c["text"])
        except (KeyError, TypeError):
            print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("unknown cmd", cmd)


if __name__ == "__main__":
    main()
