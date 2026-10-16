# Job Search Ledger

A friendly, local job search tracker built with Streamlit. Point it at a spreadsheet of your applications and it gives you a pipeline, a daily heat map, pay ranges against your target, a "needs action" list, and a weekly work search log you can download for unemployment filing (built around the Colorado CDLE format).

Everything stays on your computer. Your CSV is only read, never changed. Your status edits and notes go in a small local database.

![Overview](screenshots/1_overview.png)

## Quick start

You need Python 3.11 or newer from [python.org](https://www.python.org/downloads/).

**Windows**

1. When installing Python, tick "Add python.exe to PATH".
2. Download or clone this repo to a folder you will keep, for example `C:\Apps\job-search-ledger`.
3. Double-click `launch.bat`. The first run sets everything up (about a minute), then the ledger opens in its own window.
4. Optional desktop shortcut: right-click `create_shortcut.ps1` and choose "Run with PowerShell".

**Mac (or Linux)**

```bash
cd job-search-ledger
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Then open http://localhost:8501. It starts with fake sample data so you can look around first.

## Use your own CSV

1. Save your tracker as a CSV with these columns (extra columns are fine, blanks are fine):

   `Date Applied, Company, Position, Status, Pay Listed, Location/Remote, Source, Apply Method/ATS, Confirmation, URL, Notes, Evidence`

   `sample_data.csv` is a ready made template.
2. Copy `settings.example.json` to `settings.json` and edit it:

   ```json
   {
     "csv": "~/Documents/job_applications.csv",
     "name": "Your Name",
     "target": 90000,
     "theme": "80s Synth"
   }
   ```

   On Windows a path like `%USERPROFILE%\\Documents\\job_applications.csv` works too.
3. Start the app again. It reloads the CSV whenever the file changes, and the sidebar has a Refresh button.

Tips: any status starting with "Needs" (like "Needs action") shows up in the Needs tab. `settings.json` and the database are git ignored, so your real data never ends up in the repo. If your CSV lives in OneDrive, keep the database (`"db"`) outside OneDrive.

Every setting can also be set with an environment variable: `JOB_TRACKER_CSV`, `JOB_TRACKER_DB`, `JOB_TRACKER_TARGET`, `JOB_TRACKER_THEME`, `JOB_TRACKER_NAME`.

## Themes

Pick a theme in the sidebar and it is remembered next time. Preview one with `?theme=Y2K` in the URL.

| | | |
| --- | --- | --- |
| ![](screenshots/theme_80s_synth.png) **80s Synth** (default) | ![](screenshots/theme_90s.png) **90s** | ![](screenshots/theme_y2k.png) **Y2K** |
| ![](screenshots/theme_dark.png) **Dark** | ![](screenshots/theme_light.png) **Light** | ![](screenshots/theme_high_contrast.png) **High Contrast** |
| ![](screenshots/theme_colorblind_safe.png) **Colorblind Safe** | | |

Pay bars below your target are hatched as well as colored, so no theme relies on color alone. To add your own, copy an entry in `themes.py`, rename it and change the colors.

## More screenshots

| Applications | Needs | Weekly report |
| --- | --- | --- |
| ![](screenshots/2_applications.png) | ![](screenshots/3_needs.png) | ![](screenshots/4_weekly.png) |

All screenshots use the fake `sample_data.csv`. Regenerate them with Playwright: `python shoot.py 8501 ""` and `python shoot_themes.py 8501`.

## License

MIT. See [LICENSE](LICENSE).

---

Built by Colin Lundholm ([github.com/gitColinX](https://github.com/gitColinX)).
