import sys

f=open(sys.argv[1] if len(sys.argv)>1 else "q13_example.txt").read()
b=f.split("\n\n")
t1=0
t2=0
for m in b:
 l=m.strip().split("\n")
 a=l[0].split(":")[1].split(",")
 ax=int(a[0].split("+")[1]);ay=int(a[1].split("+")[1])
 c=l[1].split(":")[1].split(",")
 bx=int(c[0].split("+")[1]);by=int(c[1].split("+")[1])
 p=l[2].split(":")[1].split(",")
 px=int(p[0].split("=")[1]);py=int(p[1].split("=")[1])
 d=ax*by-ay*bx
 for k in range(2):
  X=px+(10000000000000 if k else 0)
  Y=py+(10000000000000 if k else 0)
  na=X*by-Y*bx
  nb=ax*Y-ay*X
  if na%d==0 and nb%d==0:
   i=na//d;j=nb//d
   if i>=0 and j>=0:
    if k:t2+=3*i+j
    else:t1+=3*i+j
print(t1)
print(t2)
