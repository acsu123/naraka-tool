# Naraka Tool

A Windows companion app for **Naraka: Bladepoint** — game tuning, a player-stats profile with shareable cards, region-locked Photobooth import, safe system tweaks, client swapping between game editions, and a native Twitch Drops farmer. One native desktop window, bilingual UI (**EN** / **VI**).

*Ứng dụng đồng hành trên Windows cho **Naraka: Bladepoint** — tinh chỉnh game, xem hồ sơ chỉ số người chơi kèm xuất card chia sẻ, chuyển đổi Photobooth bị khóa vùng, tinh chỉnh hệ thống an toàn, đổi bản game (SEA/Global/Epic/VNG), và tool auto-farm Twitch Drops. Một cửa sổ desktop, giao diện song ngữ (**EN** / **VI**).*

> Not affiliated with 24 Entertainment or NetEase. For personal use only.
> *Không liên kết với 24 Entertainment hay NetEase. Chỉ dùng cho mục đích cá nhân.*

---

## Table of contents / Mục lục

- [Features / Tính năng](#features--tính-năng)
- [Requirements / Yêu cầu](#requirements--yêu-cầu)
- [Running / Chạy chương trình](#running--chạy-chương-trình)
- [Feature guide / Hướng dẫn từng tính năng](#feature-guide--hướng-dẫn-từng-tính-năng)
- [Disclaimer / Miễn trừ trách nhiệm](#disclaimer--miễn-trừ-trách-nhiệm)

---

## Features / Tính năng

| Tab | EN | VI |
|---|---|---|
| **Game Setting** | Boot-config FPS tuning (a curated set of Unity engine flags, tunable GC time-slice) + the hidden Character Physics toggle. Game Launch button lives here. | Tinh chỉnh FPS qua boot.config (bộ flag Unity engine, GC time-slice tùy chỉnh) + bật Character Physics ẩn. Nút Khởi động game cũng ở đây. |
| **Profile** | Sign in with Steam to pull your real Naraka+ stats: career/rank per game mode (all 9 modes, hierarchical Solo/Duo/Trios selector), match history with full detail (kills, hooks, hits, weapons, soul jades, team honors), hero & weapon breakdowns, an analytics chart — and a **player-card composer** (4 themes, 4 aspect ratios, pick your stats/hero/weapon art) you can save as PNG or copy to clipboard. | Đăng nhập bằng Steam để lấy chỉ số Naraka+ thật: xếp hạng/sự nghiệp theo từng chế độ (đủ 9 mode, chọn Solo/Duo/Trios phân cấp), lịch sử trận đấu chi tiết (kill, số lần móc, đòn trúng, vũ khí, hồn ngọc, chiến tích đội), thống kê tướng & vũ khí, biểu đồ phân tích — và **trình tạo card người chơi** (4 giao diện, 4 tỉ lệ khung hình, chọn chỉ số/ảnh tướng/vũ khí) để lưu PNG hoặc sao chép. |
| **Photobooth** | Convert CN Photobooth share QR codes to Global-compatible ones, then route through a local CN gateway proxy so the game accepts the import. | Chuyển đổi mã QR Photobooth từ bản CN sang tương thích bản Global, sau đó định tuyến qua proxy CN cục bộ để game chấp nhận import. |
| **Tweaks** | 46 reversible Windows/registry tweaks across 6 categories (Performance, Gaming, GPU, Window, System, Optional) with one-click Recommended, per-tweak revert, and a full revert-all + restore point. Includes an NVIDIA Control Panel per-program settings guide. | 46 tinh chỉnh Windows/registry có thể hoàn tác, chia 6 nhóm (Hiệu năng, Gaming, GPU, Cửa sổ, Hệ thống, Tùy chọn), áp dụng khuyến nghị 1 chạm, hoàn tác từng mục hoặc tất cả + tạo điểm khôi phục. Kèm hướng dẫn cài đặt NVIDIA Control Panel theo từng ứng dụng. |
| **Swap** | Capture and switch between installed game editions (Steam / Epic / VNG / NetEase) without reinstalling — capture each edition's SDK files once, then swap instantly. | Lưu và chuyển đổi giữa các bản game đã cài (Steam / Epic / VNG / NetEase) mà không cần cài lại — lưu file SDK từng bản một lần, sau đó đổi tức thì. |
| **Twitch** | Native, in-process Twitch Drops auto-farmer for Naraka: Bladepoint — device-code login, watches and claims drops automatically, no external app required. | Tool auto-farm Twitch Drops tích hợp sẵn cho Naraka: Bladepoint — đăng nhập bằng mã thiết bị, tự động "xem" và nhận drop, không cần ứng dụng ngoài. |
| **Settings** | Language switch, Start with Windows, optional local-only Discord Rich Presence. | Đổi ngôn ngữ, khởi động cùng Windows, Discord Rich Presence cục bộ (tùy chọn). |
| **Open Web Features** | Sidebar button opens the companion web page for extra features. | Nút ở sidebar mở trang web đồng hành cho các tính năng bổ sung. |

---

## Requirements / Yêu cầu

- Windows 10 / 11
- Python 3.11+

Install dependencies / Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
flask
pywebview
Pillow
opencv-python
numpy
qrcode[pil]
zxing-cpp
requests
mitmproxy
aiohttp       # native Twitch Drops miner
pypresence    # optional: Discord Rich Presence
```

---

## Running / Chạy chương trình

```bash
python main.py
```

The UI is a local web app rendered inside a native desktop window (pywebview) — a small local Flask server runs on a fixed, uncommon port (`49517`, auto-bumped to the next free port if taken), separate from the CN Proxy's port (`8080`).

*Giao diện là một web app cục bộ hiển thị trong cửa sổ desktop gốc (pywebview) — một server Flask nhỏ chạy ở cổng cố định, ít dùng (`49517`, tự động dò cổng trống kế tiếp nếu bị chiếm), tách biệt với cổng của CN Proxy (`8080`).*

Settings (language, tokens, toggles) are stored per-user in `%LOCALAPPDATA%\NarakaTool\settings.json`.

*Cài đặt (ngôn ngữ, token, các công tắc bật/tắt) được lưu theo từng người dùng tại `%LOCALAPPDATA%\NarakaTool\settings.json`.*

---

## Feature guide / Hướng dẫn từng tính năng

### Game Setting

1. Pick your platform (Steam / Epic / VNG / Custom) — used for both Physics and Boot Config.
   *Chọn nền tảng (Steam / Epic / VNG / Tùy chỉnh) — dùng chung cho Physics và Boot Config.*
2. **Boot Config · FPS**: pick a GC time-slice preset (Smooth / Balanced / Max FPS) or type a custom value, then **Apply**. Fully reversible — **Restore Original** brings back your original `boot.config`.
   *Chọn mức GC time-slice có sẵn (Smooth / Balanced / Max FPS) hoặc nhập giá trị tùy chỉnh, rồi **Áp dụng**. Có thể hoàn tác hoàn toàn — **Khôi phục gốc** sẽ trả lại `boot.config` ban đầu.*
3. **Character Physics**: click **Enable Physics** (or **Auto Scan** to find every installation on your drives automatically).
   *Nhấn **Bật Physics** (hoặc **Auto Scan** để tự động tìm mọi bản cài trên ổ đĩa).*

### Profile

1. Click **Sign in with Steam** (opens a native login window) — or paste a session token manually if you already have one.
   *Nhấn **Đăng nhập bằng Steam** (mở cửa sổ đăng nhập gốc) — hoặc dán token phiên nếu đã có sẵn.*
2. Browse your career stats, switch game mode (parent group → Solo/Duo/Trios) and season, scroll heroes/weapons/match history, click any card for full detail.
   *Xem chỉ số sự nghiệp, đổi chế độ chơi (nhóm chính → Solo/Duo/Trios) và mùa giải, cuộn xem tướng/vũ khí/lịch sử trận, nhấn vào bất kỳ thẻ nào để xem chi tiết.*
3. Click **Create Card** to open the card composer: pick a theme, aspect ratio, hero/weapon art and 3–8 stats, then **Save PNG** or **Copy** to clipboard.
   *Nhấn **Tạo Card** để mở trình soạn card: chọn giao diện, tỉ lệ khung hình, ảnh tướng/vũ khí và 3–8 chỉ số, rồi **Lưu PNG** hoặc **Sao chép** vào clipboard.*

### Photobooth

1. Get a CN Photobooth screenshot (the one with the QR code).
   *Chụp ảnh màn hình Photobooth bản CN (ảnh có mã QR).*
2. Click **Select & Convert** and pick the image(s) — converted images appear in `converted/`.
   *Nhấn **Chọn & Chuyển đổi** và chọn ảnh — ảnh đã chuyển đổi xuất hiện trong thư mục `converted/`.*
3. Log into the game, **then** enable the CN Proxy toggle.
   *Đăng nhập vào game, **sau đó** mới bật CN Proxy.*
4. In-game, import the converted QR.
   *Trong game, import mã QR đã chuyển đổi.*

> Enable the proxy **after** logging in — enabling before login may cause authentication issues. Disable VPN / GearUp before enabling.
> *Bật proxy **sau khi** đã đăng nhập — bật trước khi đăng nhập có thể gây lỗi xác thực. Tắt VPN / GearUp trước khi bật.*

### Tweaks

Browse by category, toggle individual tweaks, or click **Recommended** to apply every tweak marked safe. **Revert All** undoes everything; **Restore Point** creates a Windows system restore point first.

*Duyệt theo từng nhóm, bật/tắt từng tinh chỉnh, hoặc nhấn **Khuyến nghị** để áp dụng mọi tinh chỉnh an toàn. **Hoàn tác tất cả** sẽ hủy mọi thay đổi; **Tạo điểm khôi phục** tạo điểm khôi phục hệ thống Windows trước khi áp dụng.*

Some tweaks require Administrator privileges (marked with an **Admin** badge); GPU tweaks are paired with a manual NVIDIA Control Panel guide since per-program NVCP profiles can't be set safely from a script.

*Một số tinh chỉnh cần quyền Administrator (có nhãn **Admin**); tinh chỉnh GPU đi kèm hướng dẫn cài NVIDIA Control Panel thủ công vì không thể chỉnh cấu hình theo từng ứng dụng một cách an toàn bằng script.*

### Swap

1. Point it at your game install folder (auto-detect or browse).
   *Chỉ định thư mục cài đặt game (tự động dò hoặc duyệt chọn).*
2. **Capture** each edition once while it's the active one — this saves that edition's SDK files.
   *Nhấn **Lưu (Capture)** cho từng bản một lần khi bản đó đang hoạt động — thao tác này lưu lại file SDK của bản đó.*
3. After capturing at least two editions, **Switch** between them any time, or **Launch** directly from a card.
   *Sau khi lưu ít nhất hai bản, có thể **Chuyển đổi (Switch)** giữa chúng bất cứ lúc nào, hoặc **Khởi động** trực tiếp từ thẻ tương ứng.*

### Twitch

Click **Start**, then activate the device code shown at the Twitch link (or use **Activate**) to sign in. Once logged in it watches and claims Naraka: Bladepoint drops automatically in the background. **Stop** ends the session.

*Nhấn **Bắt đầu**, sau đó kích hoạt mã thiết bị hiển thị tại đường link Twitch (hoặc nhấn **Kích hoạt**) để đăng nhập. Sau khi đăng nhập, tool sẽ tự động "xem" và nhận drop của Naraka: Bladepoint ở chế độ nền. **Dừng** để kết thúc phiên.*

### Settings

Switch language (EN/VI), toggle **Start with Windows**, and optionally enable **Discord Rich Presence** (shows an In-Game/Idle status on your Discord — local only, no telemetry).

*Đổi ngôn ngữ (EN/VI), bật/tắt **Khởi động cùng Windows**, và tùy chọn bật **Discord Rich Presence** (hiển thị trạng thái In-Game/Idle trên Discord — chỉ chạy cục bộ, không gửi dữ liệu đi đâu cả).*

---

## Disclaimer / Miễn trừ trách nhiệm

This tool is intended for personal use with your own account, to work around regional restrictions and tune your own client. Use at your own risk. Not affiliated with 24 Entertainment or NetEase.

*Công cụ này dành cho mục đích cá nhân với tài khoản của chính bạn, nhằm khắc phục giới hạn theo khu vực và tinh chỉnh client của bạn. Tự chịu rủi ro khi sử dụng. Không liên kết với 24 Entertainment hay NetEase.*
