from scapy.all import rdpcap, TCP, Raw
import pandas as pd
import numpy as np
import hashlib

PCAP_FILE = "data/replay_attack.pcapng"
WINDOW_SIZE = 0.2
LABEL = "replay_attack"

packets = rdpcap(PCAP_FILE)

# Filter Modbus TCP packets
filtered = []
for pkt in packets:
    if pkt.haslayer(TCP):
        sport = int(pkt[TCP].sport)
        dport = int(pkt[TCP].dport)
        if sport == 502 or dport == 502:
            filtered.append(pkt)

if len(filtered) == 0:
    raise SystemExit("No Modbus packets found")

packets = filtered

pkt_times = np.array([float(pkt.time) for pkt in packets])
pkt_sizes = np.array([len(pkt) for pkt in packets])

payload_hashes = []
for pkt in packets:
    if pkt.haslayer(Raw):
        payload_hashes.append(
            hashlib.md5(bytes(pkt[Raw].load)).hexdigest()
        )
    else:
        payload_hashes.append(None)

start_time = pkt_times[0]
end_time = pkt_times[-1]

rows = []
current = start_time

while current < end_time:
    mask = (pkt_times >= current) & (pkt_times < current + WINDOW_SIZE)
    idx = np.where(mask)[0]

    if idx.size == 0:
        current += WINDOW_SIZE
        continue

    sizes = pkt_sizes[idx]
    times = pkt_times[idx]

    if times.size > 1:
        inter_arrivals = np.diff(times)
    else:
        inter_arrivals = np.array([0.0])

    window_hashes = [payload_hashes[i] for i in idx if payload_hashes[i]]
    dup_ratio = 0.0
    if len(window_hashes) > 1:
        dup_ratio = 1.0 - (len(set(window_hashes)) / len(window_hashes))

    row = {
        "packet_count": int(idx.size),
        "bytes_total": int(sizes.sum()),
        "packet_size_mean": float(sizes.mean()),
        "packet_size_std": float(sizes.std()),
        "iat_mean": float(inter_arrivals.mean()),
        "iat_std": float(inter_arrivals.std()),
        "dup_payload_ratio": dup_ratio,
        "label": LABEL
    }

    rows.append(row)
    current += WINDOW_SIZE

df = pd.DataFrame(rows)
out_file = f"features_{LABEL}.csv"
df.to_csv(out_file, index=False)
print("Saved:", out_file)
