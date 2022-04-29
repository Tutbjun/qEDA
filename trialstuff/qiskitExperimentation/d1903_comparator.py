import string
from qiskit import *
from qiskit.circuit.library.standard_gates import *
import numpy as np
usedBits = 3
qnumbr = 5*usedBits-1
all = list(range(qnumbr))
#aList = all[0:usedBits]
#bList = all[aList[-1]+1:aList[-1]+1+usedBits]
#cList = all[bList[-1]+1:bList[-1]+1+usedBits]
#dList = all[cList[-1]+1:cList[-1]+1+usedBits]
#eList = all[dList[-1]+1:dList[-1]+usedBits]

def defComp(compare : QuantumCircuit, stringLen : int):
    bComp = QuantumCircuit(4, name='b-comp')
    bComp.x(1)
    bComp.ccx(0,1,2)
    bComp.x([0,1])
    bComp.ccx(0,1,3)
    bComp.x(0)

    aList = list(range(0,stringLen*4+1,5))
    bList = list(range(1,stringLen*4-1,5))
    cList = list(range(2,stringLen*4+1,5))
    dList = list(range(3,stringLen*4+1,5))
    eList = list(range(4,stringLen*4+1,5))

    for i in range(stringLen):
        compare.append(bComp,[aList[i],bList[i],cList[i],dList[i]])
    compare.barrier()
    for i in range(stringLen-1):
        compare.x([cList[i],dList[i]])
        compare.ccx(cList[i],dList[i],eList[i])
        compare.x([cList[i],dList[i]])
    compare.barrier()
    for i in range(stringLen-1):
        compare.ccx(cList[i+1],eList[i],cList[i])
        compare.ccx(dList[i+1],eList[i],dList[i])
    


if __name__ == '__main__':
    compare = QuantumCircuit(qnumbr,0, name='comp')
    defComp(compare,usedBits)

    c = QuantumCircuit(qnumbr,0)
    inA = '01110100111'
    inA = inA[:usedBits]
    inB = '01110100101'
    inB = inB[:usedBits]
    for i,s in enumerate(inA):
        if s == '1':
            c.x(i) 
    for i,s in enumerate(inB):
        if s == '1':
            c.x(i+usedBits) 
    c.barrier()
    c.append(compare,all)
    #c.cx(outs[-1],outs[-1]+1)
    #c.append(compare.inverse(),all[:-1])
    
    compare.draw(output='mpl', filename='out_compare.png')
    c.draw(output='mpl', filename='out.png')
    backend = Aer.get_backend('unitary_simulator')
    job = execute(c, backend)
    result = job.result()
    print(np.round(result.get_unitary(c, decimals=2),2))
    backend = Aer.get_backend('statevector_simulator')
    result = backend.run(transpile(c, backend), shots=10000).result()
    print(np.round(result.get_statevector(c),2))
    counts = result.get_counts()
    #for k in counts.keys():
    #    counts[k]/=1000
    print(counts)