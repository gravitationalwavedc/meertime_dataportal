

def get_band(freq, bw):
    if (bw == 544.0) and (freq < 816) and (freq > 815):
        rcvr = "UHF"
    elif (freq < 1284) and (freq > 1283):
        rcvr = "LBAND"
    elif (bw == 875.0) and (freq < 2189) and (freq > 2185):
        rcvr = "SBAND_0"
    elif (bw == 875.0) and (freq < 2408) and (freq > 2404):
        rcvr = "SBAND_1"
    elif (bw == 875.0) and (freq < 2627) and (freq > 2623):
        rcvr = "SBAND_2"
    elif (bw == 875.0) and (freq < 2845) and (freq > 2841):
        rcvr = "SBAND_3"
    elif (bw == 875.0) and (freq < 3064) and (freq > 3060):
        rcvr = "SBAND_4"
    else:
        rcvr = None
    return rcvr