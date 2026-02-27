from scapy.all import rdpcap, sendp, Ether
import time

PCAP_FILE = "data/replay_source.pcapng"
INTERVAL = 0.02  # seconds between replays (adjust)

pkts = rdpcap(PCAP_FILE)

# Keep only L2 packets that can be re-sent (Ether layer)
pkts = [p for p in pkts if p.haslayer(Ether)]

print(f"Loaded {len(pkts)} packets to replay")

# Replay loop
for p in pkts:
    sendp(p, verbose=False)
    time.sleep(INTERVAL)

print("Replay complete")