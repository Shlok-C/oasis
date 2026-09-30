-- computing our first DLA

X = matrix{{0,1},{1,0}}
Y = matrix{{0,-ii},{ii,0}} 
Z = matrix{{1,0},{0,-1}}
bracket = (A,B) -> A*B-B*A
bracket(X,Y)
bracket(X,Z)
bracket(Y,Z)
restart
R = frac (QQ[I, s2]/(I^2 +1, s2^2-2))
X = matrix{{0_R,1},{1,0}}
Y = matrix{{0_R,-I},{I,0}} 
Z = matrix{{1,0_R},{0,-1}}
bracket = (A,B) -> A*B-B*A
dla = {Y, 1/(s2)*(X+Z)}
dla = unique(dla |flatten apply(dla, yy-> apply(dla, xx-> bracket(xx, yy))))
M = transpose matrix apply(dla, xx->  flatten entries reshape(R^4,R^1,xx))
rank M
dla = unique(dla |flatten apply(dla, yy-> apply(dla, xx-> bracket(xx, yy))))
M = transpose matrix apply(dla, xx->  flatten entries reshape(R^4,R^1,xx))
rank M

dla = unique(dla |flatten apply(dla, yy-> apply(dla, xx-> bracket(xx, yy))))
M = transpose matrix apply(dla, xx->  flatten entries reshape(R^4,R^1,xx))
rank M


mingens image M
ker M
M_{0,1,3}
dla = unique flatten apply(dla_{0,1,3}, xx->apply(dla_{0,1,3},yy->   bracket(xx,yy)))
M = transpose matrix apply(dla, xx->  flatten entries reshape(R^4,R^1,xx))
mingens image M
ker M
M_{0,1,3}
