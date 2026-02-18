class DataPacket:
    def __init__(self):
        self.ticks_ms:int = 0
        self.vbat:float = 0.0
        self.pitch_rate:int = 0
        self.roll_rate:int = 0
        self.yaw_rate:int = 0
        self.pitch_angle:int = 0
        self.roll_angle:int = 0
        self.gforce:float = 0.0
        self.input_throtte:int = 0
        self.input_pitch:int = 0
        self.input_roll:int = 0
        self.input_yaw:int = 0
        self.m1_throttle:int = 0
        self.m2_throttle:int = 0
        self.m3_throttle:int = 0
        self.m4_throttle:int = 0
        self.lrecv_ms:int = 0

    def unpack(self, data:bytes) -> None:

        # extract timestamp (in ms)
        ticks_ms:int = data[0] << 16 | data[1] << 8 | data[2]

        # extract battery reading
        # the battery voltage will come in 10x what it is - so 168 would be 16.8, 60 would be 6.0
        # so just divide by 10 to get the actual value (as a float)
        vbat:float = data[3] / 10

        # rates
        pitch_rate:int = data[4] - 128
        roll_rate:int = data[5] - 128
        yaw_rate:int = data[6] - 128

        # angles
        pitch_angle:int = data[7] - 128
        roll_angle:int = data[8] - 128

        # gforce
        gforce:int = data[9] / 10 # divide by 10 because it is stored as 10x what it is, like vbat!

        # inputs
        input_throttle:int = data[10]     # flat percentage (0-100)
        input_pitch:int = data[11] - 100  # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
        input_roll:int = data[12] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives
        input_yaw:int = data[13] - 100   # flat percentage (-100 to 100), stored as a uint8, so subtract out 100 to allow negatives

        # motor throttles
        m1_throttle:int = data[14]
        m2_throttle:int = data[15]
        m3_throttle:int = data[16]
        m4_throttle:int = data[17]

        # last received command control pack, in ms ago
        # it is encoded in increments of 10, so multiply by 10!
        lrecv_ms:int = data[18] * 10

        # Save all
        self.ticks_ms = ticks_ms
        self.vbat = vbat
        self.pitch_rate = pitch_rate
        self.roll_rate = roll_rate
        self.yaw_rate = yaw_rate
        self.pitch_angle = pitch_angle
        self.roll_angle = roll_angle
        self.gforce = gforce
        self.input_throtte = input_throttle
        self.input_pitch = input_pitch
        self.input_roll = input_roll
        self.input_yaw = input_yaw
        self.m1_throttle = m1_throttle
        self.m2_throttle = m2_throttle
        self.m3_throttle = m3_throttle
        self.m4_throttle = m4_throttle
        self.lrecv_ms = lrecv_ms

def unpack_log(log_path:str) -> list[DataPacket]:

    # extract data from the file
    f = open(log_path, "rb")
    data:bytes = f.read()
    f.close()

    # unpack each, one by one
    lines:list[bytes] = data.split("\r\n".encode())
    packets:list[DataPacket] = []
    for p in lines:
        if len(p) > 0:
            try:
                dp:DataPacket = DataPacket()
                dp.unpack(p)
                packets.append(dp)
            except Exception as ex:
                print("Unpacking a frame failed. Skipping. Err: " + str(ex))
    
    return packets

class ArmedFlightStats:
    def __init__(self):
        self.began_at:float = None           # When the armed flight began (timestamp), in seconds
        self.ended_at:float = None           # When the armed flight ended (timestamp), in seconds
        self.vbat_max:float = None           # max vbat during flight
        self.vbat_min:float = None           # min vbat during flight
        self.gforce_max:float = None         # highest g-force experienced during flight
        self.gforce_min:float = None         # lowest g-force experienced during flight
        self.throttle_avg:float = None       # average throttle input during flight
        self.lrecv_max_ms:int = None         # max last received time, in ms
        self.lrecv_avg_ms:int = None         # average lrecv time, in ms

    @property
    def duration_seconds(self) -> float:
        if self.began_at == None or self.ended_at == None:
            return None
        else:
            return self.ended_at - self.began_at


def ExtractStats(packets:list[DataPacket]) -> list[ArmedFlightStats]:

    # Step 1: group the into armed groups
    ArmedFlights:list[list[DataPacket]] = []
    current:list[DataPacket] = None
    for packet in packets:
        if packet.input_throtte > 0:
            if current == None:
                current = []
            current.append(packet)
        else: # throttle = 0 (unarmed)
            if current != None:
                ArmedFlights.append(current)
                current = None

    # still one in the chamber? If so, log it
    if current != None:
        ArmedFlights.append(current)

    # Step 2: extract stats from each group
    ToReturn:list[ArmedFlightStats] = []
    for group in ArmedFlights:

        stats:ArmedFlightStats = ArmedFlightStats()

        # find min/max data
        for packet in group:
            
            # began
            if stats.began_at == None or (packet.ticks_ms / 1000) < stats.began_at:
                stats.began_at = packet.ticks_ms / 1000
            
            # ended
            if stats.ended_at == None or (packet.ticks_ms / 1000) > stats.ended_at:
                stats.ended_at = packet.ticks_ms / 1000

            # vbat min
            if stats.vbat_min == None or packet.vbat < stats.vbat_min:
                stats.vbat_min = packet.vbat

            # vbat max
            if stats.vbat_max == None or packet.vbat > stats.vbat_max:
                stats.vbat_max = packet.vbat

            # gforce min
            if stats.gforce_min == None or packet.gforce < stats.gforce_min:
                stats.gforce_min = packet.gforce

            # gforce max
            if stats.gforce_max == None or packet.gforce > stats.gforce_max:
                stats.gforce_max = packet.gforce

            # lrecv max
            if stats.lrecv_max_ms == None or packet.lrecv_ms > stats.lrecv_max_ms:
                stats.lrecv_max_ms = packet.lrecv_ms

        # throttle avg
        throttles:list[int] = []
        for packet in group:
            throttles.append(packet.input_throtte)
        stats.throttle_avg = sum(throttles) / len(throttles)

        # lrecv avg
        lrecvs:list[int] = []
        for packet in group:
            lrecvs.append(packet.lrecv_ms)
        stats.lrecv_avg_ms = int(round(sum(lrecvs) / len(lrecvs), 0))

        # add this stats to list
        ToReturn.append(stats)
        
    # return!
    return ToReturn