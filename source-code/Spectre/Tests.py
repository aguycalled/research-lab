# Test suite for Spectre

import random
import unittest
from Spectre import *

class TestBlock(unittest.TestCase):
    def test_block(self):
        B = Block()
        self.assertEqual(B.data, {'children':[]})
        self.assertEqual(B.ident, "")
        self.assertEqual(B.parents, [])
        params = {'data':{'children':[]}, 'ident':"Blue"}
        C = Block(params)
        self.assertEqual(C.data, {'children':[]})
        self.assertEqual(C.ident, "Blue")
        self.assertEqual(C.parents, [])
        B.parents.append(C.ident)
        assert C.ident in B.parents

class TestBlockDAG(unittest.TestCase):
    def test_addBlock(self):
        G = BlockDAG()
        genBlock = Block()
        n = 0
        genBlock.ident = str(n)
        G.addBlock(genBlock)
        n += 1
        prevBlock = genBlock
        
        while n < 100:
            params = {'data':{'children':[]}, 'ident':str(n)}
            nextBlock = Block(params)
            nextBlock.parents.append(prevBlock)
            if len(G.nodes) > 1:
                k = random.choice(list(G.nodes.keys()))
                nextBlock.parents.append(G.nodes[k])
            G.addBlock(nextBlock)
            prevBlock = nextBlock
            n += 1

    def test_getPast(self):
        G = None
        G = BlockDAG()
        A = []
        genBlock = Block()
        n = 0
        genBlock.ident = str(n)
        A.append(genBlock)
        self.assertEqual(A[0].ident, genBlock.ident)

        G.addBlock(A[0])
        self.assertEqual(G.nodes[A[0].ident].ident, A[0].ident)
        self.assertEqual(G.nodes[A[0].ident].ident, genBlock.ident)
        
        n += 1
        params = {'data':{'children':[]}, 'ident':str(n)}
        A.append(Block(params))
        A[1].parents.append(A[0])
        self.assertEqual(len(A[1].parents),1)
        self.assertTrue(A[0] in A[1].parents)
        G.addBlock(A[1])
        self.assertEqual(len(G.nodes[A[1].ident].parents), 1)
        print("All keys = ", G.nodes.keys())
        print("Parents of latest block = ", G.nodes[A[1].ident].parents)
        self.assertTrue(G.nodes[A[0].ident].ident in G.nodes[A[1].ident].parents)

        n += 1
        params = {'data':{'children':[]}, 'ident':str(n)}
        A.append(Block(params))
        self.assertEqual(A[2].parents, [])
        A[2].parents.append(A[0])
        self.assertEqual(A[2].parents, [A[0]])
        self.assertEqual(len(A[2].parents),1)
        self.assertTrue(A[0] in A[2].parents)

        G.addBlock(A[2])
        self.assertEqual(G.nodes[A[2].ident].parents, [G.nodes[A[0].ident]])
        self.assertTrue(G.nodes[A[0].ident] in G.nodes[A[2].ident].parents)
        self.assertEqual(G.nodes[A[2].ident].parents, [G.nodes[A[0].ident]])
        self.assertEqual(len(G.nodes[A[2].ident].parents),1)       

        n += 1
        params = {'data':{'children':[]}, 'ident':str(n)}
        A.append(Block(params))
        A[3].parents.append(A[2])
        self.assertEqual(len(A[3].parents),1)
        self.assertTrue(A[2] in A[3].parents)
        self.assertEqual(A[2].parents, [A[0]])
        self.assertEqual(len(A[2].parents),1)
        self.assertTrue(A[0] in A[2].parents) 

        G.addBlock(A[3])
        self.assertEqual(len(G.nodes[A[3].ident].parents),1)
        self.assertTrue(G.nodes[A[2].ident] in G.nodes[A[3].ident].parents)
        self.assertEqual(G.nodes[A[2].ident].parents, [G.nodes[A[0].ident]])
        self.assertEqual(len(G.nodes[A[2].ident].parents),1)
        self.assertTrue(G.nodes[A[0].ident] in G.nodes[A[2].ident].parents)

        n += 1
        params = {'data':{'children':[]}, 'ident':str(n)}
        A.append(Block(params))
        A[4].parents.append(A[3])
        A[4].parents.append(A[1])
        self.assertEqual(A[2].parents, [A[0]])
        self.assertEqual(len(A[2].parents),1)
        self.assertTrue(A[0] in A[2].parents)   
        self.assertEqual(len(A[4].parents),2)
        self.assertTrue(A[3] in A[4].parents)
        self.assertTrue(A[1] in A[4].parents)

        G.addBlock(A[4])
        self.assertEqual(G.nodes[A[2].ident].parents, [G.nodes[A[0].ident]])
        self.assertEqual(len(G.nodes[A[2].ident].parents),1)
        self.assertTrue(G.nodes[A[0].ident] in G.nodes[A[2].ident].parents)
        self.assertEqual(len(G.nodes[A[4].ident].parents),2)
        self.assertTrue(G.nodes[A[3].ident] in G.nodes[A[4].ident].parents)
        self.assertTrue(G.nodes[A[1].ident] in G.nodes[A[4].ident].parents)

        self.assertEqual(A[2].parents, [A[0]])
        self.assertEqual(len(A[2].parents),1)
        self.assertTrue(A[0] in A[2].parents)

        self.assertEqual(G.nodes[A[2].ident].parents, [G.nodes[A[0].ident]])
        self.assertEqual(len(G.nodes[A[2].ident].parents),1)
        self.assertTrue(G.nodes[A[0].ident] in G.nodes[A[2].ident].parents)

        P = G.getPast(A[1].ident)
        self.assertEqual(len(P.nodes),1)

        self.assertEqual(A[2].parents, [A[0]])
        self.assertEqual(len(A[2].parents),1)
        self.assertTrue(A[0] in A[2].parents) 
        self.assertTrue(A[1] not in A[2].parents)  

        P = G.getPast(A[2].ident)
        self.assertEqual(len(P.nodes),1)

        P = G.getPast(A[3].ident)
        self.assertEqual(len(P.nodes),2)

        P = G.getPast(A[4].ident)
        self.assertEqual(len(P.nodes),4)
    
        
        
        while n < 10:
            params = {'data':{'children':[]}, 'ident':str(n)}
            nextBlock = Block(params)
            nextBlock.parents.append(genBlock)
            if len(G.nodes) > 1:
                k = random.choice(list(G.nodes.keys()))
                nextBlock.parents.append(G.nodes[k])
            G.addBlock(nextBlock)
            n += 1
            if n == 10:
                distinguishedBlock = nextBlock

        
            
        


tests = [TestBlock, TestBlockDAG]
for test in tests:
    unittest.TextTestRunner(verbosity=2,failfast=True).run(unittest.TestLoader().loadTestsFromTestCase(test))
