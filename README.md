# 🌲 Valheim Mod Auto-Translator

Hey there! If you enjoy playing Valheim with mods like **Path of Valheiman**, **Adventure Backpacks**, or other community mods, but wish they were translated into your native language (like German, Russian, French, Spanish, and more)—this tool is for you!

It automatically translates your mods while ensuring game code, colors, and formatting tags (like `{0}`, `{key.use}`, `<color=...>`, and `<b>`) stay completely safe and intact.

---

## 📋 What You Need Before Starting

You only need **one thing** installed on your computer: **Python**.

1. Download **Python 3.10+** from [python.org](https://www.python.org/downloads/) (or install it from the Windows Microsoft Store).
2. ⚠️ **The Only Critical Step During Installation**:
   When the installer opens, **check the box at the bottom** that says:
   > ☑ **"Add python.exe to PATH"**
   *(If you skip this box, Windows won't recognize Python when you double-click the file!)*
3. **No extra setup or dependencies**: You don't need `pip`, virtual environments, or third-party packages. It runs 100% portable out of the box using Python's standard library.

---

## 🚀 Step-by-Step Walkthrough

The easiest way to use this tool is to drop it directly into your mod profile folder. Here is the exact step-by-step:

### Step 1: Open Your Mod Profile Folder
* **r2modman / Thunderstore Mod Manager**:
  1. Open your mod manager and choose your Valheim profile.
  2. Click **Settings** on the left sidebar.
  3. Click **"Browse profile folder"** (opens your profile directory in File Explorer).
* **Gale Mod Manager**:
  1. Click your active profile's menu/folder icon and select **Open profile folder**.
* **Manual / Vanilla Installation**:
  1. Open your main Valheim game directory (where `valheim.exe` and `BepInEx` live).

> 💡 **Quick Check**: Inside this folder, you should see a folder named `BepInEx`. That's how you know you're in the right place!

---

### Step 2: Add the Tool to Your Profile
From your downloaded zip archive, copy these two files directly into that profile folder:
* `mod_localization_translator.py`
* `run_translation.bat`

---

### Step 3: Run the Translator
Double-click **`run_translation.bat`**. The tool will guide you through simple prompts where **pressing Enter selects the recommended default**:

#### 1. Pick Your Mod
The tool auto-scans your `BepInEx/plugins/` directory and displays all installed mods with localizations:
```text
==============================================================================
                 VALHEIM MOD AUTO-TRANSLATION TOOL
==============================================================================
[Profile Context] Detected BepInEx: F:\Gale\valheim\profiles\CaveheimS3\BepInEx

Discovered 3 mod(s) with localization in your profile:
------------------------------------------------------------------------------
 [ 1] PathOfValheiman                 | [ 3] LongshipUpgrades               
 [ 2] AdventureBackpacks              |                                     
------------------------------------------------------------------------------
  [ 0] Custom File / Drag & Drop       | [ F] Filter / Search mods by name
==============================================================================
Select mod number [default: 1]: 
```
* Type the number of your mod and press **Enter** (or press Enter for default `1`).
* *The tool automatically selects the most comprehensive master dictionary file (e.g. `english.txt` with all 26,000+ lines including all skill tree deeds, perks, and bonuses).*

#### 2. Select Source & Target Language
```text
Enter source language code [default: en]: [Press Enter]
Enter target language code (e.g. de, ru, fr): de
Output filename [default: german.txt]: [Press Enter]
```

#### 3. Choose Resumption Mode
The tool analyzes your existing files and reports the exact translation breakdown:
```text
==============================================================================
                 TRANSLATION STATUS DETECTED
==============================================================================
  -> Translated lines (Genuine)       : 2,401
  -> Lines currently still in English : 23,909
  -> Completely missing lines         : 0
==============================================================================

How would you like to proceed?
  [1] Keep translated lines, translate all 23,909 remaining/English lines (Default)
  [2] Keep existing translations as-is (translate ONLY 0 completely missing lines)
  [3] Re-translate everything from scratch (ignore existing files)
Select mode [default: 1]: [Press Enter]
```
* **Option 1 (Default)**: Reuses all completed translations instantly (zero wait time) and queues only the unfinished or English lines.

#### 4. Select Translation Engine
```text
Translation Engine:
  [1] Google Translate (Default - Fast & Free, auto-switches to MyMemory if throttled)
  [2] DeepL API (Requires Free DeepL Key - 1M free chars, Best Quality & 0 rate limits)
  [3] Microsoft Azure Translator (Requires Free Azure Key - 2M chars/mo, Fast & 0 rate limits)
  [4] MyMemory (Free - Instant bypass if Google is rate-limiting your IP)
Select engine [default: 1]: 
```

> ⚠️ **Important Note About Google & MyMemory**:
> If you are translating a huge mod (such as Path of Valheiman with 26,000+ lines), **Google and MyMemory WILL temporarily throttle your IP address** during the first run. This is normal because public scrapers have strict hourly limits. When this occurs, the tool automatically engages **Auto-Wait** with a live countdown or lets you switch IPs. For a completely uninterrupted run with zero stops, use a free **DeepL** or **Microsoft Azure** key!

#### 5. Confirm Batch Pacing
```text
Batch Pacing: A delay between batches keeps traffic under rate limits.
Enter delay in seconds between batches [default: 1.0]: [Press Enter]
```
* Default is `1.0s` for DeepL/Azure or `5.0s` for Google/MyMemory. Press **Enter** to start translating!

---

## ⚡ The DeepL Engine: 1M Free Characters & Highest Quality

For large mods like **Path of Valheiman**, **DeepL** is an outstanding option:
* **Zero Rate Limits**: Never throttles or pauses during long translation runs.
* **1 Million Free Characters**: DeepL developer accounts include a one-time free credit of **1,000,000 characters** (~50,000 lines—more than double the entire Path of Valheiman mod!).
* **10x Faster**: Uses a fast 1.0-second delay between batches.
* **Superior Quality**: Produces natural gaming and fantasy translations.

### How to Get a Free DeepL API Key (Takes 2 Minutes)
1. Visit [deepl.com/pro-api](https://www.deepl.com/pro-api).
2. Click **Try for free** under Developer / Free tier (includes 1,000,000 characters free credit).
3. In your DeepL account dashboard, go to:
   **Account** → **Account Settings** → Scroll down to **Authentication Key for DeepL API**.
4. Copy your key (it will look like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx`).

### How the Tool Remembers Your DeepL Key Safely
When you choose DeepL in the tool:
1. Paste your key into the console.
2. Press **Enter** (`y`) when asked:
   ```text
   Save key locally on this PC so you don't have to enter it again? [default: y]:
   ```
3. The tool saves your key to `BepInEx/config/.deepl_key`.
4. **On all future runs**, it automatically detects your key:
   ```text
   Found saved DeepL key (d5bf...2:fx). Use it? [default: y]:
   ```
   Just press **Enter** and you're good to go!

---

## 🔷 Microsoft Azure Translator: 2 Million Characters Free Every Month

Microsoft provides an official Translator API on Azure Cognitive Services with a permanent **Free F0 Tier** that gives you **2,000,000 characters every month**:
* **Recurring 2 Million Free Characters/Month**: Automatically refreshes every month forever.
* **Zero Rate Limits**: Fast and reliable enterprise translation.
* **10x Faster**: Uses a 1.0-second delay between batches.

### 💳 Note on Azure Sign-Up (Credit Card Verification)
> **Important**: Microsoft requires an Azure account to generate a key. During account creation, Microsoft requires a credit card to verify your identity and prevent bot abuse.
> * **You will NOT be charged**: The **F0 Free Tier** has a strict spending limit of $0. You are never billed unless you manually choose to convert to a paid pay-as-you-go subscription.

### How to Get a Free Azure Translator Key (Step-by-Step)
1. Go to the [Azure Portal](https://portal.azure.com) and log in with your Microsoft account.
2. In the search bar at the top, type **Translator** and select **Translator** (under AI + Machine Learning services).
3. Click **+ Create**:
   * **Subscription**: Select your subscription (or Free Trial).
   * **Resource Group**: Click *Create new* (e.g. `valheim-translator`).
   * **Region**: Select your closest region (e.g. `East US`, `West Europe`, or `Global`).
   * **Name**: Any unique name (e.g. `my-valheim-translator`).
   * **Pricing Tier**: Select **Free F0 (2M Characters translated per month)**.
4. Click **Review + Create**, then click **Create**.
5. Once deployment completes, click **Go to resource** → On the left menu, click **Keys and Endpoint**.
6. Copy **Key 1** and note your **Location/Region** (e.g. `eastus` or `global`).

### How the Tool Remembers Your Azure Key
When you select Microsoft Azure in the tool:
1. Paste your **Key** and type your **Region** (or press Enter for `global`).
2. Press **Enter** (`y`) when asked to save locally.
3. The tool saves your credentials securely in `BepInEx/config/.azure_key`.
4. **On future runs**, it automatically detects your key and region so you never have to re-type them!

> 🔒 **Privacy Guarantee**: 
> `.deepl_key`, `.azure_key`, `*.key`, and `.env` are protected by `.gitignore`. Your keys are stored solely on your local PC and are **never** shared, uploaded, or committed to GitHub.

---

## ☕ Handling Rate Limits & Cooldowns

Free public services (Google & MyMemory) track IP addresses and may temporarily throttle requests if you translate thousands of lines in one sitting. 

The tool handles this automatically with three flexible workarounds:

### Workaround 1: Intelligent Auto-Wait & Live Countdown (Hands-Free)
If all free engines hit a rate limit, the tool immediately saves your progress and presents:
```text
==============================================================================
[Rate Limit Alert] All free translation services are temporarily throttled on your IP.
Progress safely saved to disk! (4,200 / 23,781 strings completed)
==============================================================================
Options:
  [1] Auto-Wait: Pause and auto-resume in 45m when cooldown expires (Default)
  [2] Save & Exit: Close now safely (pick up anytime later by running again)
  [3] Hotspot/VPN: Switched to phone mobile hotspot / VPN? Press Enter to retry immediately.
```
* If you pick **`[1] Auto-Wait`** (or just press **Enter**), a live countdown bar starts ticking:
  ```text
  Cooling down IP... Resuming in 44m 12s [====--------------------] (Ctrl+C to exit)
  ```
* When the timer reaches 0, the script wakes up and **resumes translating automatically**!
* You can press `Ctrl+C` at any time to save and exit without losing a single line.

---

### Workaround 2: The 5-Second Phone Hotspot / VPN Reset (Instant)
Rate limits on free web services are tied strictly to your **internet IP address**, not your computer or identity.

1. Turn on your smartphone's **Mobile Hotspot**.
2. Connect your PC to the hotspot (or toggle a VPN server).
3. Your PC gets a brand new IP address in 5 seconds.
4. Select **`[3] Hotspot/VPN`** (or **Reset Cooldown** at startup) and press **Enter**—**your rate limit is instantly reset to 0**!

---

### Workaround 3: DeepL or Microsoft Azure Free Keys
Switch to DeepL (Option `2`) or Microsoft Azure (Option `3`) in the engine menu to bypass Google/MyMemory IP limits entirely.

---

## 🛡️ Why You Are Never Left With Broken or Partial Files

A major concern players have is ending up with broken, half-translated game files. Here is how this tool protects you:

1. **Instant Real-Time Caching**: Every batch of 50 strings is written directly to disk and saved to `.cache.json` immediately.
2. **Safe Game Fallback**: If translation stops partway through, any unfinished lines safely retain their original English text. Valheim will load the file without crashing, and you will never see broken internal tags (like `@skill_bonus_402`).
3. **One-Click Resumption**: When you re-run the tool later, Option 1 (`Keep translated lines, translate remaining lines`) is selected by default. It skips the completed lines and picks up exactly where it stopped.

---

## 🎮 How to See It in Valheim

1. Start Valheim (or leave it running!).
2. Go to **Settings** → **Language** → Select your language (e.g. *Deutsch*).
3. **Instant Hot-Reload Trick (No Game Restart Required)**:
   * If Valheim is already running, switch the in-game language to English and then switch it right back to your language.
   * Valheim immediately reloads all translation files from disk!
4. Jump into your world and enjoy your mods in your language! 🍻

---

## 🔄 What Happens When a Mod Updates?

When a mod developer releases an update with new skills, items, or quests:

* **Your Translations Survive Mod Updates**: The tool writes to both the mod's plugin folder and your profile's `BepInEx/config/<ModName>.translations/` folder. Mod managers (Thunderstore, Gale, r2modman) **never erase the config folder**, so your translations are permanently preserved.
* **Updating is Instant**:
  1. Double-click `run_translation.bat`.
  2. All unchanged lines are reused instantly from your cache in milliseconds.
  3. Only the brand new strings are translated.
  4. Mod updates finish in just a few seconds!

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

## 💬 Share With the Mod Community!

Once you've translated a mod, share your translation file in the mod developer's Discord channel! Community developers appreciate translations and often package them into official releases so players worldwide can benefit.
