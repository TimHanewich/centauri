# Centauri "How it started, how it's going" video

## Clips
- Started
    - **clip_1** - 0:16 of this video (showing Scout): https://www.youtube.com/watch?v=W7-yFK6OCB0
    - **clip_2** - 0:45 of this video (toppling over): https://www.youtube.com/watch?v=W7-yFK6OCB0
    - **clip_3** - 3:25 of this video (crash out): https://www.youtube.com/watch?v=Bj0aN_1-mIM
    - **clip_4** - 5:55:55 of this video (throwing goggles): https://www.youtube.com/watch?v=W7-yFK6OCB0
    - **clip_5** - 5:53:30 of this video (shaking head): https://www.youtube.com/watch?v=W7-yFK6OCB0
    - **clip_6** - 7:16 in this video (spazzing out inside): https://www.youtube.com/watch?v=44tEmUwnbl4
    - **clip_7** - 8:51 in this video (falls and burns): https://www.youtube.com/watch?v=PfZOqbugjq8
    - **clip_8** - 0:00 in this video (Scout flipping out): https://www.youtube.com/watch?v=ziMcRW0sNCE
    - **clip_9** - 4:08:12 in this video (staring at Scout frusturated): https://www.youtube.com/watch?v=W7-yFK6OCB0
    - **clip_10** - 5:28:09 in this video (balancing on hands): https://www.youtube.com/watch?v=W7-yFK6OCB0
    - **clip_11** - 11:06 of this video (propeller pops off inside): https://www.youtube.com/watch?v=yjyKg9pMgkc
    - **clip_l2** - 27:37 in this video (Centauri crashing and breaking arm at Nokomis Park): https://www.youtube.com/watch?v=I0SOVnilZ6g
- Going
    - **clip_13** - 0:46 of this video (dad flyby at OJT): https://www.youtube.com/watch?v=LzWieMo0hrw
    - **clip_14** - 3:23 of this video (flying above townhome roof onboard, reverse): https://www.youtube.com/watch?v=xKoLI-wi2mM
    - **clip_15** - 5:14 of this video (steep bank onboard): https://www.youtube.com/watch?v=xKoLI-wi2mM
    - **clip_16** - 0:48 of this video (bay street park fly by): https://www.youtube.com/watch?v=cTK0w3Zb9RU
    - **clip_17** - 1:28 of this video (flying over trees to see water @ Vamo Park): https://www.youtube.com/watch?v=ZYWoqG6bNVE
    - **clip_18** - 3:50 of this video (acceleration and asending in field): https://www.youtube.com/watch?v=oEOU1fnXip0
    - **clip_19** - 5:16 of this video (quick fly by in field): https://www.youtube.com/watch?v=oEOU1fnXip0
    - **clip_20** - 5:57 of this video (up close): https://www.youtube.com/watch?v=oEOU1fnXip0
    - **clip_21** - 17:45 of this video (up close then pivot away): https://www.youtube.com/watch?v=mi2_N91XVpg
    - **clip_22** - 13:45 of this video (launch away and fly to the right): https://www.youtube.com/watch?v=mi2_N91XVpg
    - **clip_23** - 12:10 of this video (shoot off overhead): https://www.youtube.com/watch?v=mi2_N91XVpg
    - **clip_24** - 12:20 of this video (airbrake): https://www.youtube.com/watch?v=mi2_N91XVpg
    - **clip_25** - 12:03 of this video (flying into distance on Michelle iPhone): https://www.youtube.com/watch?v=oEOU1fnXip0
    - **clip_26** - 16:45 of this vidoe (flying by Michelle in curve): https://www.youtube.com/watch?v=oEOU1fnXip0

To download portions of video with yt-dlp: 
- Downloads between 15:15 and 16:15 (1 minute)
- Downloads best quality `.mp4` with best quality audio
- Outputs to `clip_a.mp4`
```
yt-dlp --download-sections "*00:15:15-00:16:15" -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" https://www.youtube.com/watch?v=oEOU1fnXip0 -o clip_2.mp4
```

## Audio
Music from here: https://www.youtube.com/watch?v=PtSAnQdlzpc

```
yt-dlp -f "bestaudio[ext=m4a]" --extract-audio "https://www.youtube.com/watch?v=PtSAnQdlzpc" -o "music.m4a"
```