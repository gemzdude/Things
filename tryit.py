from random import randint

d = { "1": "one", "2":"two","3":"three"}
g = list(d.keys())
endpnt = len(d)


def get_guess():
    global g, endpnt
    which = randint(0, endpnt-1)
    txt = g[which]
    g[which] = g[endpnt-1]
    endpnt = endpnt - 1
    return txt


while True:
    print(g)
    x = input("hit enter or q...")
    if x == "q":
        break
    print(get_guess())
    if endpnt == 0:
        print("that's all")
        break


