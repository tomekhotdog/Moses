import sys

def s(f):
    g=[]
    for l in open(f):
        l=l.rstrip("\n")
        if l!="":
            g.append(list(l))
    sr=0;sc=0
    for i in range(len(g)):
        for j in range(len(g[0])):
            if g[i][j]=="^":
                sr=i;sc=j
    p1=0
    d=0
    r=sr;c=sc
    v=set()
    v.add((r,c))
    while True:
        if d==0:
            nr=r-1;nc=c
        elif d==1:
            nr=r;nc=c+1
        elif d==2:
            nr=r+1;nc=c
        else:
            nr=r;nc=c-1
        if nr<0 or nr>=len(g) or nc<0 or nc>=len(g[0]):
            break
        if g[nr][nc]=="#":
            d=(d+1)%4
            continue
        r=nr;c=nc
        v.add((r,c))
    p1=len(v)
    cnt=0
    for i in range(len(g)):
        for j in range(len(g[0])):
            if g[i][j]=="#":
                continue
            if i==sr and j==sc:
                continue
            if (i,j) not in v:
                continue
            g[i][j]="#"
            r=sr;c=sc;d=0
            seen=set()
            seen.add((r,c,d))
            loop=0
            while True:
                if d==0:
                    nr=r-1;nc=c
                elif d==1:
                    nr=r;nc=c+1
                elif d==2:
                    nr=r+1;nc=c
                else:
                    nr=r;nc=c-1
                if nr<0 or nr>=len(g) or nc<0 or nc>=len(g[0]):
                    break
                if g[nr][nc]=="#":
                    d=(d+1)%4
                    if (r,c,d) in seen:
                        loop=1
                        break
                    seen.add((r,c,d))
                    continue
                r=nr;c=nc
                if (r,c,d) in seen:
                    loop=1
                    break
                seen.add((r,c,d))
            if loop==1:
                cnt+=1
            g[i][j]="."
    print(p1)
    print(cnt)

s(sys.argv[1])
