## Major Commits in this Repo
|Commit|Description|
|-|-|
|`880aef867fc2f1b2ec5d29fdde0b9acc81f665ad`|Increased fidelity on complementary fiter tuning (`alpha`).|
|`bb82f6d966d11feddc39d52769fcd9ced6e6cf36`|Refined trigonometry performed by flight controller: improved atan2 and square-root optimization. Also improved timestamp use.|
|`5c853569c82e61e2295a4fad8cb94631c98f1d2d`|Updated checksum algorithm to Fletcher16 for improved avoidance of corrupt control packets|
|`61bab17eb4d671a2d8fb203ce7eb0f3bf9620548`|Flight Controller minor correction: keep gyro readings used for flight control separate from euler-adjusted for angle estimation, making the angle estimation more accurate. **THIS IS THE FINAL VERSION OF CENTAURI QUADCOPTER V1!**|