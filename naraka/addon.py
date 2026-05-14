import json
import datetime
import requests
from urllib.parse import parse_qs, urlparse

from mitmproxy import http

NARAKA_HOST      = "www.narakathegame.com"
NARAKA_PATH      = "/h5/20260401/yingpengfx/"
NARAKA_API_HOST  = "api.narakathegame.com"
API_HOST         = "api.yjwujian.cn"
API_PATH         = "/yjwj/studio_share/game_detail"
CONVERTED_SUFFIX = "CONVERTED"


def _fetch_api(share_code: str) -> dict | None:
    url = f"https://api.yjwujian.cn/yjwj/studio_share/game_detail?shareCode={share_code}"
    try:
        s = requests.Session()
        s.trust_env = False
        resp = s.get(
            url, timeout=30,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
        return resp.json()
    except Exception:
        return None


class NarakaAddon:

    def __init__(self, log_queue=None, debug=False):
        self._q     = log_queue
        self._debug = debug

    def _log(self, msg: str):
        if not self._debug:
            return
        line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        if self._q is not None:
            try:
                self._q.put_nowait(line)
            except Exception:
                pass

    def response(self, flow: http.HTTPFlow):
        if flow.request.pretty_host != NARAKA_API_HOST:
            return
        if API_PATH not in flow.request.path:
            return

        self._log(f"response → bypass hook fired  {flow.request.pretty_host}{flow.request.path[:60]}")

        try:
            data = json.loads(flow.response.content.decode("utf-8"))
        except Exception:
            self._log("response → JSON parse failed")
            return

        d = data.get("data")

        if not d:
            parsed    = urlparse(flow.request.path)
            params    = parse_qs(parsed.query, keep_blank_values=True)
            codes     = params.get("shareCode", [])
            share_code = codes[0] if codes else None
            if not share_code:
                self._log("response → no shareCode in URL, cannot fallback")
                return
            if CONVERTED_SUFFIX in share_code:
                share_code = share_code.replace(CONVERTED_SUFFIX, "")
            self._log(f"response → data=None, fallback fetch for shareCode={share_code}")
            fetched = _fetch_api(share_code)
            if not fetched:
                self._log("response → fallback _fetch_api returned None")
                return
            fd = fetched.get("data")
            if fd:
                fetched["message"] = "Success"
                fd["playerId"]     = "32fs0000000000000000000"
                fd["playerName"]   = "QR Convert Thành Công | from Wang with ❤️"
                fd["reviewStatus"] = 2
            body = json.dumps(fetched, ensure_ascii=False).encode("utf-8")
            flow.response = http.Response.make(
                200, body,
                {
                    "content-type":                "application/json; charset=utf-8",
                    "content-length":              str(len(body)),
                    "access-control-allow-origin": "*",
                }
            )
            self._log("response → fallback synthetic response injected  reviewStatus=2")
            return

        if d.get("reviewStatus") == 2:
            self._log("response → reviewStatus already 2, no patch needed")
            return

        d["reviewStatus"] = 2
        d["playerName"]   = "QR Bypass Thành Công | from Wang with ❤️"

        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        flow.response.content                    = body
        flow.response.headers["content-type"]   = "application/json; charset=utf-8"
        flow.response.headers["content-length"] = str(len(body))
        self._log("response → patched  reviewStatus=2")


addons = [NarakaAddon()]
