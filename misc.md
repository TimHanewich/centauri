## Major Development Milestones
These commits mark key milestones in Centauri's development. Each represents a completion of a significant improvement, usually to a functional component of the Centauri ecosystem. I note them here in case you wanted to "rewind" back to a version you are building! *Note: if the commit is noted here, it has been flown, tested, and validated to work!*
|Commit|Description|
|-|-|
|`880aef867fc2f1b2ec5d29fdde0b9acc81f665ad`|Flight Controller update: increased fidelity on complementary fiter tuning (`alpha`).|
|`bb82f6d966d11feddc39d52769fcd9ced6e6cf36`|Flight Controller update: Refined trigonometry performed by flight controller: improved atan2 and square-root optimization. Also improved timestamp use.|
|`5c853569c82e61e2295a4fad8cb94631c98f1d2d`|Flight Controller & Transmitter update: Updated checksum algorithm to Fletcher16 for improved avoidance of corrupt control packets|
|`61bab17eb4d671a2d8fb203ce7eb0f3bf9620548`|Flight Controller minor correction: keep gyro readings used for flight control separate from euler-adjusted for angle estimation, making the angle estimation more accurate. **THIS IS THE FINAL VERSION OF CENTAURI QUADCOPTER V1!**|
|`1f67a8ac6fce3acbb701287ff98ccbec55b04caa`|Added accelerometer calibration correction|