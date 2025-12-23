# Dashware Assets
I have used [Dashware](https://dashware.software.informer.com/) for overlaying telemetry data on top of a video file. I include the reusable assets here:
- [Project Template](./project/) - place this in the projects directory (`\Documents\DashWare Projects`) and then rename the folder to whatever you want to call the project. When you open it in Dashware, it will prompt you to find the `data.csv` and `video.MP4` files.
    - This project contains all you need **Centauri data profile**, **Gauges**, etc.

## Important Note About Timing
I noticed while recording on the DVR on my FPV monitor, I just wasn't able to get the telemetry Centauri logs synced with the video. And the desync appeared to be worse further into the video, as time goes on.

I believe this is because the DVR on the FPV monitor is of very poor quality and actually records slower than the passage of time, causing this issue. I went and compared the "armed" duration on the telemetry and the "armed" duration on the monitor-recorded video (just timestamps on the video):
- Duration of Armed in Telemetry: **268.956** seconds
- Duration of Armed in Video: **270.133**

So, as we can see above, the video is *longer* than the actual telemetry! It is 0.44% longer! This can for-sure cause a desync issue!

So, in this scenario, the solution I used was to *slow down* the video just a tad so the arm begin and arm end times of the video *match* the telemetry data. We can do the math on this and se that to make this adjustment, I would have to stretch the video to 99.564165844% of its original time. 

To do this, I calculated what the *correct* duration of the total clip should be, in seconds. Then, with that in mind, I calculated what the Minutes:Seconds:Frames timestamp should be in premiere pro (i.e. at 30 FPS). I calculated that, placed my sequence time there, and then used Premiere Pro's **Rate Stretch Tool** to "stretch" the video to end at that time exactly, with the difference being sped up/slowed down automatically!

![stretch](https://i.imgur.com/Kuu30Fc.png)

## Having an issue with syncing up telemetry over a FPV Monitor/Goggle DVR Footage? Here is the fix!
Using FFMPEG, "trim out" a clip of the flight you want to use. This will trim out the video, set it to a constant frame rate and do so in lossless quality:

```
ffmpeg -i onboard.AVI -ss 00:07:20 -to 00:11:00 -vf "fps=30" -q:v 1 flight6.avi
```

After this, in Premiere Pro, compare the total flight duration (duration while "armed") between the telemetry (recorded by Microcontroller) and the FPV video. More likely than not, the FPV video will be *longer* than the telemetry. I believe this is because the video recording is slow.

Calculate the time the video *should end* by doing some math (seen above). Use the rate tool in Premiere Pro (**on the constant frame rate export!**) to adjust the time length of the video to the target duration (to match the telemetry) and then position it in a widescreen format.