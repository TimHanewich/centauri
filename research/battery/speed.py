import time
import gc

vbat_u16:int = 39256 # input
vbat:int = 0 # declare vbat so it doesnt use up memory later when we declare it (throws off our test)

# old way: ~135 us, 0 bytes used
vbat:int = (vbat_u16 * 33) // 11820

# new way: ~135 us, 0 bytes used
vbat:int = ((-248065 + (vbat_u16 * 297)) + 50_000) // 100_000