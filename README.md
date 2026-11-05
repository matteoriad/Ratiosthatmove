# ratios that move: daily reel pipeline

Every day at 10:00 Berlin time, GitHub Actions picks the next episode in `episodes/queue/`,
renders the Reel (illustrated dishes, molecule close-ups, gliding ingredient bars, synth
music) and its covers, and publishes it to Instagram as a Reel. Nothing runs on your laptop.

```
episodes/queue/     one JSON per episode (ep01, ep02, …); see WRITING.md
posted.json         log of what has been posted (episode, media id, permalink, time)
foodreel.py         episode timeline, frames, covers, synth music, render
library.py          illustrations, ingredient icons, molecule scenes
brand.py            colours, type, drawing helpers
pipeline/post.py    render → upload → publish → record in posted.json
pipeline/gate.py    decides whether a run posts (10:00 Berlin, once a day)
pipeline/check.py   validates new episodes and renders stills to look at
.github/workflows/daily-reel.yml   triggers: post-now push, backup schedule, manual run
.github/post-now    a push that changes this file posts the next episode
```

## How it runs

- **Daily trigger (Claude scheduled task, ~09:30 Berlin):** writes a timestamp to
  `.github/post-now` and pushes. The workflow's gate waits until 10:00 and posts.
- **Backup:** scheduled runs at :41 in three UTC hours. They post only if nothing went out
  in the last 6 hours, so there is never more than one post a day.
- **Weekly writer (Claude scheduled task, Sundays):** tops the queue up to ~14 unposted
  episodes (max 7 per run), checks them, pushes them and sends a summary.
- If a run fails, GitHub emails you.

## One-time setup

### 1. Instagram account
Create @ratiosthatmove, then in the app: Settings → Account type and tools →
**Switch to professional account** → Creator. The account must be public.

### 2. Meta app + token (Facebook-login setup)
New Meta apps no longer show "API setup with Instagram login", so use the Facebook-login setup:
1. **Facebook Page:** create a Page ("ratios that move") and link @ratiosthatmove:
   Page → Settings → Linked accounts → Instagram → Connect.
2. developers.facebook.com → your app (the chordsthatmove app works too) → Use cases →
   Instagram API → **API setup with Facebook login** → **Add required content permissions**.
3. **Tools → Graph API Explorer** → Get User Access Token with `instagram_basic`,
   `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`,
   `business_management`. When Facebook asks which Pages/accounts, include the new
   ratios that move Page and Instagram account.
4. ⓘ next to the token → **Open in Access Token Tool** → **Extend Access Token** → paste the
   long-lived token back into the Explorer.
5. Run `GET me/accounts?fields=name,access_token,instagram_business_account`. For the
   ratios that move Page:
   - `instagram_business_account.id` → `IG_USER_ID`
   - `access_token` (Page token, never expires) → `IG_ACCESS_TOKEN`

### 3. Repository secrets
Repo → Settings → Secrets and variables → Actions → New repository secret:
`IG_USER_ID` and `IG_ACCESS_TOKEN`. Secrets stay private even though the repo is public
(it has to be public so Instagram can fetch the cover from raw.githubusercontent.com).
Never put the token in a file or in a chat.

### 4. Test, then go live
- Actions → **Daily reel** → Run workflow with **dry run** ticked → download the `reel`
  artifact (video, covers, caption) and check it.
- Run again with dry run unticked to post episode 1 right away. From then on it posts by
  itself every day.

## Previewing locally

```
pip install numpy pillow pycairo requests        # plus ffmpeg
python3 foodreel.py episodes/queue/ep01-breakfast-batters.json test.mp4
python3 foodreel.py episodes/queue/ep01-breakfast-batters.json test --cover
python3 foodreel.py episodes/queue/ep01-breakfast-batters.json test --stills 2 6 12
python3 pipeline/check.py --stills /tmp/stills
```
