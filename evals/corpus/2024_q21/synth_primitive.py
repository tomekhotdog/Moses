import sys

def go(c):
    n="789456123 0A"
    p={}
    for i in range(12):
        if n[i]!=" ":
            p[n[i]]=(i%3,i//3)
    d=" ^A<v>"
    q={}
    for i in range(6):
        if d[i]!=" ":
            q[d[i]]=(i%3,i//3)
    def exp(s,m,g):
        cur="A"
        out=""
        for ch in s:
            x1,y1=m[cur]
            x2,y2=m[ch]
            dx=x2-x1
            dy=y2-y1
            h=""
            if dx<0:
                h+="<"*(-dx)
            v=""
            if dy<0:
                v+="^"*(-dy)
            if dy>0:
                v+="v"*dy
            if dx>0:
                h+=">"*dx
            # pick order that avoids gap
            a=h+v if dx<0 else v+h
            # check the chosen order against gap
            cx,cy=x1,y1
            ok=True
            for mv in a:
                if mv=="<":cx-=1
                elif mv==">":cx+=1
                elif mv=="^":cy-=1
                elif mv=="v":cy+=1
                if (cx,cy)==g:
                    ok=False
            if not ok:
                b=v+h if dx<0 else h+v
                a=b
            out+=a+"A"
            cur=ch
        return out
    s1=exp(c,p,(0,3))
    s2=exp(s1,q,(0,0))
    s3=exp(s2,q,(0,0))
    return len(s3)

def main():
    f="example.txt"
    if len(sys.argv)>1:
        f=sys.argv[1]
    t=0
    for line in open(f):
        c=line.strip()
        if c=="":
            continue
        num=0
        for ch in c:
            if ch>="0" and ch<="9":
                num=num*10+int(ch)
        t+=go(c)*num
    print(t)

main()
