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

# Look for native WON and LOST outcomes on the same fixed tower level.
send(2,"I",8);read("B")
import math
for angle in [22,15,30,10,35,40,8,45,50,55,60,65,70,75,80,5,0,-5,85,18,25,27,32,38,42]:
    fx=round(98-55*math.cos(math.radians(angle)))
    fy=round(253+55*math.sin(math.radians(angle)))
    send(31,"iiii",fx,fy,0,0);read("B")
    for i in range(120):
        send(12);state,=read("B")
        if state in (6,7):break
        time.sleep(.2)
    send(65);score,=read("I")
    print("shot",angle,fx,fy,"state",state,"score",score,flush=True)
    if state in (6,7):
        result=out/("win.json" if state==6 else "loss.json")
        if not result.exists():
            result.write_text(json.dumps([fx,fy,state,score]))
    if (out/"win.json").exists() and (out/"loss.json").exists():break
    send(51,"I",1);read("B")
    for i in range(80):
        time.sleep(.15);send(12);state,=read("B")
        if state==5:break
    time.sleep(.6)
