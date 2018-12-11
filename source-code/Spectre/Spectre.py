from collections import deque

class Block(object):
    def __init__(self, params={'data':{'children':[]}, 'ident':""}):
        self.data = params['data']
        self.ident = params['ident']
        self.parents = []

def sumVotes(X, pair, theseVotes, k):
    (yid, zid) = pair
    a, b, c, result = 0, 0, 0, None
    for xid in X.nodes:
        if (xid, yid, zid) in theseVotes:
            if theseVotes[(xid,yid,zid)]==1:
                a += 1
            elif theseVotes[(xid,yid,zid)]==0:
                b += 1
            elif theseVotes[(xid,yid,zid)]== -1:
                c += 1
    m = max(a,b,c)
    result = None
    if m==a and m != b and m != c:
        result = 1
    elif m==b and m != a and m != c:
        result = 0
    elif m==c and m != a and m != b:
        result = -1
    elif m == a and m == b and m != c:
        result = 1
    elif m == a and m == c and m != b:
        result = 0
    elif m== b and m == c and m != a:
        result = -1
    elif m == a and m == b and m == c:
        result = 0
    return result

class BlockDAG(object):
    def __init__(self, params=None):
        self.nodes = {}
        self.leaves = {}
        self.genBlockID = None   
        self.cachedPasts = {}
        self.cachedFutures = {}     
    
    def addBlock(self, newNode, allowableIdents=None):
        # add newNode if newNode.ident is allowable, and its children
        if len(self.nodes)==0:
            self.nodes.update({newNode.ident:newNode})
            self.leaves.update({newNode.ident:newNode})
            self.genBlockID = newNode.ident
            for c in newNode.data['children']:
                self.addBlock(c, allowableIdents)
        elif newNode.ident not in self.nodes:
            if (allowableIdents is not None and newNode.ident in allowableIdents) or allowableIdents is None:
                goodParents = True
                for p in newNode.parents:
                    goodParents = goodParents and p.ident in self.nodes
                if goodParents:
                    self.nodes.update({newNode.ident:newNode})
                    self.leaves.update({newNode.ident:newNode})
                    for p in newNode.parents:
                        if newNode not in p.data['children']:
                            p.data['children'].append(newNode)
                            if p.ident in self.leaves:
                                del self.leaves[p.ident]
                    for c in newNode.data['children']:
                        self.addBlock(c, allowableIdents)
    
    def getPast(self, nodeIdent):
        result = BlockDAG()
        if nodeIdent in self.cachedPasts:
            result = self.cachedPasts[nodeIdent]
        else:
            node = self.nodes[nodeIdent]
            if len(node.parents) > 0:
                print(str(nodeIdent) + ", " + str([p.ident for p in node.parents]))
                Q = deque()
                pids = []
                for p in node.parents:
                    if p.ident not in pids:
                        Q.append(p)
                while(len(Q)>0):
                    x = Q.popleft()
                    if x.ident not in pids:
                        pids.append(x.ident)
                        print("pids = ", pids)
                    for p in x.parents:
                        Q.append(p)
                #print("pids = ", pids)
                result.addBlock(self.nodes[self.genBlockID], pids)
                self.cachedPasts.update({nodeIdent:result})
        return result

    def getFuture(self, nodeIdent):
        result = BlockDAG()
        if nodeIdent in self.cachedFutures:
            result = self.cachedFutures[nodeIdent]
        else:
            node = self.nodes[nodeIdent]
            result.addBlock(node)
            self.cachedFutures.update({nodeIdent:result})
        return result
            
    def getOrder(xid,yid):
        b = None
        x = self.nodes[xid]
        Px = self.getPast(x)
        if yid in Px.nodes:
            b = -1
        else:
            Fx = self.future(x)
            if yid in Fx.nodes:
                b = 1
            else:
                b = 0
        return b
                
    def vote(self, k):
        result, votes, Q, touched = {}, {}, deque(), []
        for xid in self.leaves:
            x = self.leaves[xid]
            Q.append((x,k))
        while len(Q)>0:
            (x,j) = Q.popleft()
            xid = x.ident
            if x not in touched and j > 0:
                touched.append(x)
                for y in x.parents:
                    Q.append((y,j-1))
                P = self.getPast(x)
                pv = P.vote(j-1)
                F = self.getFuture(x)
                for yid in self.nodes:
                    for zid in self.nodes:
                        if yid in P.nodes and zid in P.nodes:
                            newVotes = { (xid, yid, zid):pv[(yid,zid)], (xid, zid, yid):pv[(zid,yid)], (xid, yid, xid):1,  (xid, xid, yid):-1,  (xid, zid, xid):1,  (xid, xid, zid):-1 }
                        elif yid in P.nodes and zid not in P.nodes:
                            newVotes = { (xid, yid, zid):1, (xid, zid, yid):-1, (xid, yid, xid):1,  (xid, xid, yid):-1,  (xid, zid, xid):-1,  (xid, xid, zid):1 }
                        elif yid not in P.nodes and zid in P.nodes:
                            newVotes = { (xid, yid, zid):-1, (xid, zid, yid):1, (xid, yid, xid):-1,  (xid, xid, yid):1,  (xid, zid, xid):1,  (xid, xid, zid):-1 }
                        elif yid not in P.nodes and zid not in P.nodes:
                            sv = sumVotes(F.nodes,(yid,zid),votes, k)
                            newVotes = { (xid, yid, zid):sv, (xid, zid, yid):-1*sv, (xid, yid, xid):-1,  (xid, xid, yid):1,  (xid, zid, xid):-1,  (xid, xid, zid):1 }
                        votes.update(newVotes)
                for yid in self.nodes:
                    for zid in self.nodes:
                        sv = sumVotes(self, (y,z), votes, k)
                        newResult = {(yid,zid):sv, (zid,yid):-1*sv}
                        result.update(newResult)
                return result

    def spec(B, k):
        # B = linearly ordered blockdag with nodes in self
        result = {}
        v = self.vote(k)
        for yid in self.nodes:
            for zid in self.nodes:
                if yid in B and zid in B:
                    w = self.getOrder(yid,zid)
                    newResult = {(yid,zid):w, (zid,yid):-1*w}
                elif yid in B and zid not in B:
                    newResult = {(yid,zid):1, (zid,yid):-1}
                elif yid not in B and zid in B:
                    newResult = {(yid,zid):-1, (zid,yid):1}
                elif yid not in B and zid not in B:
                    newResult = {(yid,zid):v[(yid,zid)], (zid,yid):v[(yid,zid)]}
                result.update(newResult)
        return result
        






