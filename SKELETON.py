import sys
import requests
from urllib.parse import urljoin

# ========= COLOR SETUP =========
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR = True
except ImportError:
    COLOR = False

def c(text, color):
    return color + text + Style.RESET_ALL if COLOR else text

GREEN = Fore.GREEN if COLOR else ""
YELLOW = Fore.YELLOW if COLOR else ""
RED = Fore.RED if COLOR else ""
BLUE = Fore.CYAN if COLOR else ""
GRAY = Fore.LIGHTBLACK_EX if COLOR else ""

# ========= UI =========
def banner():
    print("=" * 60)
    print("  S K E L E T O N  —  Session Trust Mapper")
    print("  Purpose: Post‑Auth Session / Scope / Boundary Analysis")
    print("=" * 60)

def signal(color, tag, msg):
    icon = {
        GREEN: "✓",
        YELLOW: "!",
        RED: "✗",
        BLUE: "→",
        GRAY: "·"
    }.get(color, "*")
    print(c(f"[{icon} {tag}]", color), msg)

def explain(text):
    print(c("    ↳ " + text, GRAY))

# ========= CORE =========
def load_session():
    """
    User pastes cookies / token manually from a legitimate login.
    This keeps the tool legal and controlled.
    """
    print("\n[ Session Material Input ]")
    cookies = {}

    print("Paste cookies (key=value), empty line to finish:")
    while True:
        line = input("> ").strip()
        if not line:
            break
        if "=" in line:
            k, v = line.split("=", 1)
            cookies[k.strip()] = v.strip()

    token = input("\nOptional Authorization Bearer token (or press Enter): ").strip()

    return cookies, token

def probe_surface(name, base_url, cookies, token):
    signal(BLUE, "PROBE", f"{name} → {base_url}")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.get(
            base_url,
            headers=headers,
            cookies=cookies,
            timeout=10,
            allow_redirects=False
        )

        signal(GREEN if r.status_code < 400 else YELLOW,
               "HTTP",
               f"{r.status_code}")

        if r.status_code == 200:
            explain("Session accepted on this surface")
        elif r.status_code in (401, 403):
            explain("Session explicitly rejected")
        else:
            explain("Unexpected behavior — inspect manually")

        return {
            "surface": name,
            "status": r.status_code,
            "length": len(r.text),
            "headers": dict(r.headers)
        }

    except Exception as e:
        signal(RED, "ERROR", str(e))
        return None

def analyze_results(results):
    print("\n[ Trust Boundary Analysis ]")

    accepted = [r for r in results if r and r["status"] == 200]

    if len(accepted) > 1:
        signal(RED, "MISMATCH", "Session accepted on multiple distinct surfaces")
        explain("High‑value ATO chain candidate")
    elif len(accepted) == 1:
        signal(GREEN, "CONSISTENT", "Session scope appears constrained")
    else:
        signal(GREEN, "LOCKED", "No unintended session trust detected")

    print("\n[ Surface Summary ]")
    for r in results:
        if not r:
            continue
        signal(GRAY, r["surface"], f"HTTP {r['status']} | body {r['length']} bytes")

# ========= MAIN =========
def main():
    banner()

    if len(sys.argv) < 2:
        print("Usage: python SKELETON.py https://auth.ripio.com")
        sys.exit(1)

    auth_base = sys.argv[1].rstrip("/")

    cookies, token = load_session()

    print("\n[ Session Probing Begins ]")

    surfaces = {
        "AUTH": auth_base,
        "TRADE": "https://trade.ripio.com",
        "KYC": "https://kyc.ripio.com",
        "B2B": "https://sandbox-b2b.ripio.com"
    }

    results = []
    for name, url in surfaces.items():
        results.append(probe_surface(name, url, cookies, token))

    analyze_results(results)

    signal(GREEN, "DONE", "SKELETON analysis complete")

if __name__ == "__main__":
    main()