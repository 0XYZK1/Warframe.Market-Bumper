<p align="center">
  <img src="assets/icon.png" alt="Warframe Market Bumper" width="150">
  <h1 align="center">WARFRAME MARKET BUMPER</h1>
  <p align="center">
    <i>A <b>T A O S</b> Production.</i><br>
    The Art of Software.
  </p>
</p>

<p align="center">
  <a href="https://github.com/0XYZK1/Warframe.Market-Bumper/releases/latest"><img src="https://img.shields.io/github/v/release/0XYZK1/Warframe.Market-Bumper?color=white&labelColor=black&style=for-the-badge&logo=github&label=LATEST%20RELEASE" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Custom-white?labelColor=black&style=for-the-badge" alt="License"></a>
</p>

---

A minimalist automated bumper for warframe.market.
Keep your buy and sell listings at the top of the page so your items sell faster.

No browser automation, no login window, no API key. One token, one click, done.

### QUICKSTART

1. Download the [Latest Release](https://github.com/0XYZK1/Warframe.Market-Bumper/releases/latest) (`.exe`).
2. Run the file. No Python or setup required.
3. Paste your token and press **Update Articles**.

### AUTHENTICATION (TOKEN)

In order to bump your items, the tool needs your session token.

1. Log into [warframe.market](https://warframe.market).
2. Right-click anywhere on the page → **Inspect**.
3. Navigate to the **Application** tab.
4. In the left sidebar, expand **Cookies** and select `https://warframe.market`.
5. Look for the cookie named `JWT`.
6. Copy the long, cryptic text from the value box at the bottom.
7. Paste this token into the bumper tool.

The token is stored locally in `config.json` next to the executable. It never
leaves your machine except as the `Authorization` header sent to warframe.market.

### WHAT IT DOES

- Reads all active buy and sell orders from your account
- Re-saves each order, which moves it back to the top of the market
- Shows live progress: `UPDATING 3 OF 12...`
- Handles invalid or expired tokens with a clear error
- Remembers the last token between launches
- Ships with its own window icon, so it looks right in the taskbar

### NOTES

- Windows 10/11.
- One order is bumped roughly every 0.4 seconds to stay polite to the API.
- Your market session can expire; grab a fresh `JWT` cookie if that happens.
- This is an unofficial tool and is not affiliated with warframe.market or Digital Extremes.

---

<p align="center">
  <b>T A O S</b><br>
  <i>Design. Code. Silence.</i><br>
  <br>
  © 2026 Dox / Xyk
</p>
