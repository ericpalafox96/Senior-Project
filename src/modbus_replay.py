from pymodbus.client import ModbusTcpClient
import time

DER_IP = "172.17.201.90"
PORT = 502

client = ModbusTcpClient(DER_IP, port=PORT)
client.connect()

print("Replaying Modbus read requests...")

# Replay the SAME read multiple times (this is the replay)
for i in range(20):
    rr = client.read_holding_registers(address=0, count=4, slave=1)
    time.sleep(0.05)

client.close()
print("Replay finished")