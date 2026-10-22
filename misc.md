## Major Commits in this Repo
|Commit|Description|
|-|-|
|`880aef8`|Increased fidelity on complementary fiter tuning (`alpha`).|
|`bb82f6d`|Refined trigonometry performed by flight controller: improved atan2 and square-root optimization. Also improved timestamp use.|
|`5c85356`|Updated checksum algorithm to Fletcher16 for improved avoidance of corrupt control packets|
|`61bab17`|Flight Controller minor correction: keep gyro readings used for flight control separate from euler-adjusted for angle estimation, making the angle estimation more accurate. **THIS IS THE FINAL VERSION OF CENTAURI QUADCOPTER V1!**|