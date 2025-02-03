# FaceIt Stats for [Millennium](https://github.com/shdwmtr/millennium)  
The Millennium plugin integrates a simple FaceIt widget into profile pages viewed in the Steam web browser. **Also works in overlay!**

> [!CAUTION]  
> This plugin uses the WebKit feature to inject JavaScript code directly into your Steam web browser. **It is strongly recommended that you review the code yourself before installing this plugin.** Millennium has improved the plugin installation and moderation process, and I am currently waiting for moderator approval to download the plugin directly from the [Steambrew](https://steambrew.app/plugins) website. Avoid using untrusted builds from GitHub; however, prebuilt releases are available for easier installation.  

![image](https://github.com/alowave/millennium-faceit-stats/blob/main/example.png?raw=true)
## Installation  
1. **Download the latest release** from the repository.  
2. Copy the `faceit-stats` folder into your Steam plugins directory.  
   - Default path: `C:\Program Files (x86)\Steam\plugins`  
3. Activate a plugin in the steam (millenium) settings.

## Building  
#### For Unix-like
```bash
git clone --depth=1 https://github.com/SteamClientHomebrew/Millennium 
mv ./Millennium/examples/plugin ./plugin_template 
rm -rf Millennium

cd plugin_template
pnpm install
```

#### For Windows
```powershell
git clone --depth=1 https://github.com/SteamClientHomebrew/Millennium 
Copy-Item -Recurse .\Millennium\examples\plugin .\plugin_template
Remove-Item -Recurse -Force .\Millennium

cd plugin_template
pnpm install
```
Run the following command to build the plugin:  
```bash
pnpm run dev
```

After building, place the plugin template in your plugins directory:  
`%MILLENNIUM_PATH%/plugins/plugin_template`. Then, activate it from the "Plugins" tab in Steam, or use the command:  
```bash
millennium plugins enable faceit_stats
```

## Note  
**MILLENNIUM_PATH**:  
- For Windows: Steam installation path, e.g., `C:\Program Files (x86)\Steam`  
- For Unix: `~/.millennium`  
