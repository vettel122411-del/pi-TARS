import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# r.delete("commands")

while True:
    line = input()

    for ch in line:
        if ch == "w":
            r.rpush("commands", "forward")
        elif ch == "a":
            r.rpush("commands", "turn_left")
        elif ch == "d":
            r.rpush("commands", "turn_right")
        elif ch == "q":
            r.rpush("commands", "quit")
            break

    print(r.lrange("commands", 0, -1))

    if ch == "q":
        break
