import sys

def go(f):
    d=open(f).read().strip().split("\n")
    a=int(d[0].split(":")[1])
    b=int(d[1].split(":")[1])
    c=int(d[2].split(":")[1])
    p=[int(x) for x in d[4].split(":")[1].strip().split(",")]
    # part 1
    r=run(a,b,c,p)
    print(",".join(str(x) for x in r))
    # part 2 - quine search digit by digit
    print(p2(p))

def run(a,b,c,p):
    i=0
    o=[]
    while i<len(p):
        x=p[i]
        y=p[i+1]
        if y==0: v=0
        elif y==1: v=1
        elif y==2: v=2
        elif y==3: v=3
        elif y==4: v=a
        elif y==5: v=b
        elif y==6: v=c
        else: v=0
        if x==0:
            a=a//(2**v)
        elif x==1:
            b=b^y
        elif x==2:
            b=v%8
        elif x==3:
            if a!=0:
                i=y
                continue
        elif x==4:
            b=b^c
        elif x==5:
            o.append(v%8)
        elif x==6:
            b=a//(2**v)
        elif x==7:
            c=a//(2**v)
        i=i+2
    return o

def p2(p):
    cands=[0]
    for k in range(len(p)-1,-1,-1):
        nxt=[]
        for cc in cands:
            for d in range(8):
                aa=(cc<<3)|d
                if run(aa,0,0,p)==p[k:]:
                    nxt.append(aa)
        cands=nxt
    if cands:
        return min(cands)
    return -1

if __name__=="__main__":
    go(sys.argv[1] if len(sys.argv)>1 else "q17_example.txt")
