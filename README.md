# **FaceIt Stats for [Millennium](https://steambrew.app)**

### 🏆 Integrate a **[FaceIt](https://faceit.com)** widget with **CS2 stats** into Steam profile pages — works in overlay browser too!

![image](https://github.com/alowave/millennium-faceit-stats/blob/main/example.png?raw=true)

## ⚡ About
🔹Displays **basic Steam and FaceIt stats** (Matches, Elo, K/D ratio).

🔹**CS2 start date** is determined using the "A New Beginning" achievement, which may cause delays on profiles with many achievements. This could be improved in future updates.

💡 **Left-click the stats** to view H/S, ADR, and WinRate.

## 📥 Installation
> Avoid GitHub builds—they may be outdated and haven't been reviewed by Millennium developers.

The **preferred** method is downloading directly from [Steambrew](https://steambrew.app/plugin?id=57c553750f61). 

1.  **Download the latest release** from the plugin page.
2.  Copy the `alowave.faceit_stats` folder into your Steam plugins directory:
    -   **Default path:** `C:\Program Files (x86)\Steam\plugins`
3.  Activate the plugin in **Millennium settings**.

## 🛠️ Building
Clone the repository:
```bash
git clone https://github.com/alowave/millennium-faceit-stats
cd millennium-faceit-stats
pnpm install
```
To build the plugin:
```bash
pnpm run build
```
Then, move the plugin to your **plugins directory** and activate it in settings or via:
```bash
millennium plugins enable faceit_stats
```

## 📌 Notes
⚠️ This plugin uses **WebKit** to inject JavaScript directly into your Steam web browser. **Please review the code before installing from untrusted sources.**

### **MILLENNIUM_PATH:**
-   **Windows:** `C:\Program Files (x86)\Steam`
-   **Unix:** `~/.millennium`
