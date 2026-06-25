import sys

d=open(sys.argv[1]).read().strip().split("\n")
r=[]
for l in d:
 a=l.split(" ")
 p=a[0][2:].split(",")
 v=a[1][2:].split(",")
 r.append((int(p[0]),int(p[1]),int(v[0]),int(v[1])))

a=0;b=0;c=0;e=0
for x in r:
 nx=(x[0]+x[2]*100)%101
 ny=(x[1]+x[3]*100)%103
 if nx==50 or ny==51:continue
 if nx<50 and ny<51:a+=1
 if nx>50 and ny<51:b+=1
 if nx<50 and ny>51:c+=1
 if nx>50 and ny>51:e+=1
print(a*b*c*e)

t=0
while 1:
 t+=1
 s=set()
 f=1
 for x in r:
  nx=(x[0]+x[2]*t)%101
  ny=(x[1]+x[3]*t)%103
  if (nx,ny) in s:
   f=0
   break
  s.add((nx,ny))
 if f:
  print(t)
  break
