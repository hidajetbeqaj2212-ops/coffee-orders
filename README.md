# XBar

Order system for XBar: a floor plan of the room, rounds, split bills, regular clients, "from the house", stock, expenses, salaries, the calendar, closing the day and monthly reports.

It runs as a Windows desktop app on the bar PC. The owner can also open it from a phone or laptop, from anywhere, through Tailscale.

Receipts are order slips ("POROSI", marked *Nuk është kupon fiskal*), not fiscal receipts.

## How it works

- **The bar PC is the "server".** All data lives in a SQLite database on that PC (`%APPDATA%\XBar\data\orders.db`), and the app serves the screen to itself on `http://127.0.0.1:4848`.
- **Every screen stays live.** A change on the bar shows up on the owner's phone within a second, and the other way round.
- **The floor plan.** *Tavolinat* shows the room from above: 6 tables, 1 separe (a sofa lounge around a low table, counted as one table), the Pikado (darts) corner and the bar counter. People sit and order at the bar, so every bar stool is its own tab (*Banaku · 1*, *Banaku · 2*, …). Each table and stool shows whether it's free or busy and the running total; tables also show how long they've been open. Tap one to see or take the order.
- **Receipts print without a driver.** The receipt is rendered as an image and sent straight to the 80 mm thermal printer as ESC/POS, over the network (printer IP, port 9100) or USB. Set it in *Zyra → Sistemi*.
- **Backups** run every night and after every day close. Each one goes to `%APPDATA%\XBar\backups`, plus a copy in `OneDrive\XBar Backups` when OneDrive is signed in. The last 90 are kept.
- **Updates.** The app checks this repo's GitHub Releases, downloads new versions in the background and installs them the next time it restarts.
- **Remote access.** Any device that isn't the bar PC must log in with the owner PIN, and is only reachable over Tailscale or the café's Wi-Fi. Printing and backups can only be started from the bar PC.

## Setting up the bar PC (one time)

1. **Fix the clock.** In *Settings → Time & language → Date & time*, set the time zone to *(UTC+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague*, and turn on *Set time automatically*.
2. **Connect the receipt printer** to the network (note its IP) or by USB. No driver is needed for network printers.
3. **Install the app.** Download `XBar-Setup-x.y.z.exe` from the latest release and run it. It installs, starts by itself and opens with Windows from then on.
   - The first time it starts, Windows asks once for admin permission. This adds the firewall rule that lets the owner's phone connect.
4. **In the app, open *Zyra*** (default PIN **1234**) **→ *Sistemi*:**
   - Enter the printer's IP or pick the USB printer, and press *Printo një faturë prove*.
   - Change the owner PIN.
5. **Set up the room.** In *Zyra → Menaxhimi → Salla*, set how many tables, separe, bar stools and pillars there are, then press *Rregullo sallën* and drag each piece to where it sits in the room. Tap a piece to rotate it, change a table's shape, or mirror the bar counter. The entrance can be moved too.
6. **Menu and staff.** In *Zyra → Menaxhimi*, check the menu and prices, staff and regular clients. There is one staff profile to start with; add more under *Stafi* whenever needed. Salaries go in *Zyra → Pagat*.
7. **Turn on OneDrive.** Sign in to OneDrive with the owner's Microsoft account (free, 5 GB). *Sistemi → Backup* should then show *OneDrive: Po*.
8. **Set up Tailscale** (free):
   - Install Tailscale on the bar PC and sign in with the owner's account (Google login works).
   - Set Tailscale to start with Windows. It does this by default.
   - In the Tailscale admin console, turn off *key expiry* for the bar PC, so it never logs out.

## The owner's phone

1. Install **Tailscale** from the App Store or Play Store and sign in with the **same** account.
2. Open the browser and go to the address shown in *Zyra → Sistemi → Qasja nga larg*, for example `http://bar-pc:4848`.
3. Enter the owner PIN.
4. Add it to the home screen. It then opens like an app:
   - iPhone: *Share → Add to Home Screen*
   - Android: *⋮ → Add to Home screen*

On a phone the floor plan is turned upright so the whole room fits the screen (entrance at the bottom, bar at the top). *Lista* switches to a plain list.

## Shipping a new version

1. Change `version` in `package.json` (e.g. `1.0.1`).
2. Run `npm run build:ui` if the UI changed.
3. Commit and push to `main`.

GitHub Actions sees the new version, builds the installer and publishes the release (tag `v1.0.1`). The bar PC picks it up on its own, usually within a few hours, and installs it on the next restart. You can also press *Instalo tani* in *Sistemi*.

## Restoring data

Use *Zyra → Sistemi → Rikthe të dhënat nga një backup…* and pick a `.db` file, from the backups folder or from OneDrive. The current data is backed up first, then the app restarts with the restored data.

On a brand-new PC:
1. Install the app.
2. Restore the newest file from `OneDrive\XBar Backups`.

## Development

```
npm install
npm run dev               # server only, at http://127.0.0.1:4848 (data in .devdata/)
npm start                 # the full desktop app
npm run build:ui          # rebuild app/index.html from prototype/pos.html
```

The screen design lives in `prototype/pos.html`. `tools/build-ui.py` turns it into `app/index.html`:
- strips the demo data
- connects it to the server (`tools/boot.js`, `tools/sync.js`)
- adds the *Sistemi* tab

### Name, logo and icon

The XBar wordmark (top bar, login, receipts, PDF reports) and the app icon come from `tools/brand/brand.html` (set in Archivo, SIL Open Font License). To change them, edit that file, run `python3 tools/brand/render.py`, then `npm run build:ui`. The name itself is set in `package.json` (`productName`, `build.productName`, `build.nsis.shortcutName`), `app/manifest.webmanifest`, `app/login.html`, `electron/main.js` and the `<title>` in `tools/build-ui.py`.

Keep `build.appId` as it is once the app is installed: changing it makes Windows treat it as a different app, and its data and updates won't carry over.

### The floor plan

The room is stored with the settings (`cfg.plan`): a width of 1000 units, a depth of `plan.h` units, and each table, separe and fixture with its centre (`x`, `y`), rotation (`r`) and shape (`k`: `sq4`, `sq2`, `round`, `rect`, `high`, `stand`, `sofa`, `counter`, `col`, `door`; the counter also has `seats` and can be mirrored with `m`). Shapes are drawn in `pieceSvg()` in `prototype/pos.html`.
