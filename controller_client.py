from pymodbus.client import ModbusTcpClient
import time
import random

DER_IP = "172.17.201.90"   # مثال: "192.168.1.23"
PORT = 502

client = ModbusTcpClient(DER_IP, port=PORT)
if not client.connect():
    print("FAILED to connect to DER at", DER_IP, "port", PORT)
    raise SystemExit

print("Connected to DER:", DER_IP)

while True:
    rr = client.read_holding_registers(address=0, count=4, slave=1)
    if rr.isError():
        print("Read error:", rr)
    else:
        print("Telemetry:", rr.registers)

    # Occasionally send a command (write)
    if random.random() < 0.2:
        new_p = random.randint(400, 700)   # pretend "power setpoint"
        wr = client.write_register(address=2, value=new_p, slave=1)
        if wr.isError():
            print("Write error:", wr)
        else:
            print("Command sent: set register 2 =", new_p)

    time.sleep(0.5)
