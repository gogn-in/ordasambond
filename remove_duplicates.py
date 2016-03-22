FILE = "ordasambond/data/ordasambond.txt"

seen = {}

with open(FILE, "r") as f:
    for line in f.readlines():
        line = line.strip()
        hv = hash(line)
        if hv in seen:
            pass
            # print("Seen: {}".format(line))
        else:
            # print "Not seen: {}".format(line)
            with open("out.txt", "ab") as out:
                out.write(line + "\n")
            seen[hv] = True
