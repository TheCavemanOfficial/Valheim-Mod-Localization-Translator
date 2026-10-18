# 🌲 Valheim Mod Auto-Translator

Hey there! If you enjoy playing Valheim with mods like **Path of Valheiman**, **Adventure Backpacks**, or other community mods, but wish they were translated into your native language (like German, Russian, French, Spanish, and more)—this little tool is for you!

It automatically translates your mods while making sure game code, colors, and formatting tags (like `{0}`, `<color=...>`, and `<b>`) stay completely safe and intact.

---

## 📋 What You Need Before Starting

You only need **one thing** installed on your computer: **Python**.

1. Download **Python 3.12+** from [python.org](https://www.python.org/downloads/) (or get it from the Windows Microsoft Store).
2. ⚠️ **The Only Important Step During Installation**:
   When the installer opens, **check the little box at the bottom** that says:
   > ☑ **"Add python.exe to PATH"**
   *(If you skip this box, Windows won't know where Python is when you double-click the file!)*
3. **No extra setup needed**: You don't have to install any packages, type terminal commands, or set up API keys. It runs straight out of the box.

---

## 🚀 Step-by-Step: How to Use It

The easiest way to use this tool is to drop it right into your mod profile folder. Here’s how:

### Step 1: Open Your Mod Profile Folder
* **If you use r2modman or Thunderstore Mod Manager**:
  1. Open your mod manager and choose your Valheim profile.
  2. Click **Settings** on the left menu.
  3. Click **"Browse profile folder"** (it opens a folder window on your computer).
* **If you use Gale Mod Manager**:
  1. Click your active profile's menu/folder icon and select **Open profile folder**.
* **If you install mods manually**:
  1. Go to your main Valheim game folder (where `valheim.exe` and `BepInEx` live).

> 💡 **Quick Check**: Inside this folder, you should see a folder named `BepInEx`. That's how you know you're in the right spot!

---

### Step 2: Put the Tool Files in Your Profile
From the zip file you downloaded, copy these two files directly into that profile folder:
* `mod_localization_translator.py`
* `run_translation.bat`

---

### Step 3: Run the Tool
1. **Double-click** `run_translation.bat`.
2. A window will open and automatically look through your mods. You'll see a clean, easy-to-read list on your screen, like this:
   ```text
   ==============================================================================
                      VALHEIM MOD LOCALIZATION SCANNER
   ==============================================================================
    [ 1] Path of Valheiman               | [ 2] Adventure Backpacks
    [ 3] Longship Upgrades               | [ 0] Custom File / Drag & Drop
   ------------------------------------------------------------------------------
   Select mod number [default: 1]:
   ```
3. **Pick your mod**: Type the number of the mod you want to translate and press **Enter**.
4. **Choose your language**: Type your two-letter language code and press **Enter**:
   * `de` for German
   * `ru` for Russian
   * `fr` for French
   * `es` for Spanish
   * `pl` for Polish
   * *(See the table below for more languages!)*
5. **Pacing Delay**: It will ask about a delay between batches (default is `5.0` seconds). Press **Enter** to accept the default, or type `15.0` if you want it to translate extra gently to avoid rate limits.

---

### Step 4: Sit Back and Let It Work!
* **Everything is set up on your computer first**: Before translating a single word, the tool automatically creates the needed folders, translation files, and cache files on your computer.
* It will translate your mod in friendly batches.
* Once it reaches 100%, it automatically installs the finished translation into your mod's folder and your game config folder!

> ### ☕ What if I see a "Rate Limit Cooldown" message?
> If you are translating a huge mod with thousands of lines, Google may occasionally temporarily throttle your IP address (HTTP 429). 
> 
> **How the Tool Handles This Automatically**: 
> * **Automatic 60-Minute Cooldown**: The moment Google signals a rate limit, the tool sets a 60-minute cooldown timer saved to disk. It immediately switches to **MyMemory** and **will not hammer Google again for 60 minutes**, even if you close and restart the application!
> * **Auto-Selection on Next Launch**: If you launch the tool while the 60-minute cooldown is active, it automatically detects the remaining time and routes your translation through MyMemory without bothering Google.
> 
> **Your Translation Options**:
> 1. **Built-in MyMemory Engine**: Translates smoothly without Google. Can be picked directly as Option `2` at startup.
> 2. **DeepL Free API (Option 3)**: Register for a free DeepL API key at [deepl.com/pro-api](https://www.deepl.com/pro-api) (gives you 500,000 characters free every month with 0 rate limits). Select Option `3` at startup.
> 3. **The 5-Second Network Reset Trick (VPN / Hotspot)**: If you connect to a VPN or your phone's mobile hotspot, you get a fresh IP immediately. You can select **Reset Cooldown & Try Google** from the startup menu to test the new IP right away.
> 4. **Close It and Come Back Later**: You can safely close the window at any time (Ctrl+C). Every single translated batch is saved to disk immediately so you never lose progress.

---

### Step 5: See It in Valheim!
1. Start Valheim (or stay in-game if it's already running!).
2. Go to **Settings** → **Language** → Select your language (e.g. *Deutsch*).
3. **Hot-Reload Trick (No Game Restart Needed!)**:
   * If Valheim is already running, simply switch the language away (e.g. to English) and then switch it right back to your language.
   * Valheim will reload the localization files instantly on the spot!
4. **Verify It Worked**:
   * Open `BepInEx/LogOutput.log` and search for:
     `Localization <language>: N strings from <file>.txt`
   * You'll see the exact count of lines loaded from your translation file!
5. Jump into your world and enjoy your mod in your language! 🍻

---

## 🔄 What Happens When a Mod Updates?

When your mod gets an update with new skills or items:

* **Your Translations Always Win and Never Get Overwritten**:
  The tool installs your files into both the mod's plugin folder and your profile's config folder (e.g. `BepInEx/config/<ModName>.translations/`). Mod managers (Gale, Thunderstore, r2modman) **never touch the config folder**, so your translations survive mod updates completely intact and override whatever ships with the mod.
* **Updating with the Tool**:
  1. Double-click `run_translation.bat` again in your profile folder.
  2. The tool checks your existing translation:
     * **Unchanged lines are reused instantly from your cache** (no waiting, no re-translating).
     * **Only the brand new or changed lines** get translated.
  3. The whole update usually finishes in **just a few seconds**!

## 🧩 Translating Incomplete or Existing Files

If a mod already has a partial translation file, or you are updating an existing one, the tool automatically detects it and gives you three smart options:

1. **Option 1: Keep existing translations & translate ONLY missing/empty lines (Default)**
   * Every line that is already translated is reused instantly with **zero wait time and zero API calls**.
   * Only missing keys or empty lines are translated, completing the file.
2. **Option 2: Keep existing translations, but ALSO translate lines left in English**
   * Translators often start by copying the English file and only translate partway through.
   * This option keeps all real translations, but automatically detects lines that were left in English and translates them for you!
3. **Option 3: Re-translate everything from scratch**
   * Ignores the old file and performs a fresh, clean translation from the official English master.

---

## ⌨️ Common Language Codes

| Code | Language | Output File Name |
| :--- | :--- | :--- |
| `de` | German (Deutsch) | `german.txt` or `*.German.json` |
| `ru` | Russian (Русский) | `russian.txt` or `*.Russian.json` |
| `fr` | French (Français) | `french.txt` or `*.French.json` |
| `es` | Spanish (Español) | `spanish.txt` or `*.Spanish.json` |
| `pl` | Polish (Polski) | `polish.txt` or `*.Polish.json` |
| `it` | Italian (Italiano) | `italian.txt` or `*.Italian.json` |
| `pt-br` | Portuguese (Brazil) | `portuguese_brazilian.txt` |
| `pt-pt` | Portuguese (Europe) | `portuguese_european.txt` |
| `zh` | Chinese (简体中文) | `chinese.txt` or `*.Chinese.json` |
| `ja` | Japanese (日本語) | `japanese.txt` or `*.Japanese.json` |
| `ko` | Korean (한국어) | `korean.txt` or `*.Korean.json` |
| `tr` | Turkish (Türkçe) | `turkish.txt` or `*.Turkish.json` |
| `vi` | Vietnamese (Tiếng Việt) | `vietnamese.txt` or `*.Vietnamese.json` |
| `sv` | Swedish (Svenska) | `swedish.txt` or `*.Swedish.json` |
| `da` | Danish (Dansk) | `danish.txt` or `*.Danish.json` |
| `no` | Norwegian (Norsk) | `norwegian.txt` or `*.Norwegian.json` |
| `fi` | Finnish (Suomi) | `finnish.txt` or `*.Finnish.json` |
| `nl` | Dutch (Nederlands) | `dutch.txt` or `*.Dutch.json` |
| `cs` | Czech (Čeština) | `czech.txt` or `*.Czech.json` |
| `uk` | Ukrainian (Українська) | `ukrainian.txt` or `*.Ukrainian.json` |

---

## 💬 Share With the Mod Author!

Once you've translated a mod, consider dropping the translated file into the mod's Discord channel! Mod developers love having community translations and will often include your work officially in future updates so other players can enjoy it too.
