from pathlib import Path
import json, os, socket, struct, time

out=Path(os.environ["BIRDS_TEMP"])
for _ in range(120):
    try:
        conn=socket.create_connection(("127.0.0.1",2004),timeout=2)
        break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError("Game interface did not open port 2004")
conn.settimeout(35)
stream=conn.makefile("rb")
def send(code, fmt="", *args):
    conn.sendall(struct.pack("!B"+fmt,code,*args))
def read(fmt):
    size=struct.calcsize("!"+fmt)
    return struct.unpack("!"+fmt,stream.read(size))
send(1,"IB",1,1)
print("configure",read("BBB"))
requested=False
for _ in range(150):
    send(12)
    state,=read("B")
    print("native state",state)
    if state in (8,9,10,11):
        send(68);print("set",read("IIIIBBB"))
    elif state in (1,2,3) and not requested:
        send(51,"I",1);print("load",read("B"));requested=True
    elif state==5:
        break
    time.sleep(.4)
else:
    raise RuntimeError("Level failed to start")
send(11)
w,h=read("II")
assert 0<w<=4096 and 0<h<=4096,(w,h)
rgb=stream.read(w*h*3)
assert len(rgb)==w*h*3 and len(set(rgb))>32
(out/"kickoff.ppm").write_bytes(f"P6\n{w} {h}\n255\n".encode()+rgb)
send(62)
length,=read("I"); gt=stream.read(length)
(out/"board.json").write_bytes(gt)
print("Screenshot",w,h,"ground truth bytes",length)
