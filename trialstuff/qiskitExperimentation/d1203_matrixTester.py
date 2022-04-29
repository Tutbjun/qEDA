from qiskit import *
import numpy as np
usedBits = 3
qnumbr = 2*usedBits+3
all = list(range(qnumbr))
aList = all[0:usedBits]
bList = all[aList[-1]+1:aList[-1]+1+usedBits]
outs = all[bList[-1]+1:bList[-1]+3]
compare = QuantumCircuit(qnumbr-1,0, name='comp')


def func(circuit, i, j1, j2 = None,inverse = False):
    if j2 is not None:
        if not inverse:
            circuit.ccx(aList[i],outs[j2],outs[j1])
            circuit.ccx(bList[i],outs[j2],outs[j1])
        else:
            circuit.ccx(bList[i],outs[j2],outs[j1])
            circuit.ccx(aList[i],outs[j2],outs[j1])
    else:
        if not inverse:
            circuit.cx(aList[i],outs[j1])
            circuit.cx(bList[i],outs[j1])
        else:
            circuit.cx(bList[i],outs[j1])
            circuit.cx(aList[i],outs[j1])

commandList = []
for i in range(usedBits):
    j1 = i%2
    j2 = (i-1)%2
    if i == 0:
        commandList.append([func,[compare,i,j1]])
    else:
        commandList.append([func,[compare,i,j1,j2]])
    commandList[-1][0](*commandList[-1][1])
    compare.x(outs[j1])
    if i >= 1:
        commandList[-2][0](*commandList[-2][1])
        compare.x(outs[j2])
    compare.barrier()
compare.cx(outs[j1],outs[j2])
    

"""compare.cx(aList[0],outs[0])
compare.cx(bList[0],outs[0])
compare.x(outs[0])

compare.ccx(aList[1],outs[0],outs[1])
compare.ccx(bList[1],outs[0],outs[1])
compare.x(outs[1])
"""

c = QuantumCircuit(qnumbr,0)
inA = '01110100111'
inA = inA[:usedBits]
inB = '01010100101'
inB = inB[:usedBits]
for i,s in enumerate(inA):
    if s == '1':
        c.x(i) 
for i,s in enumerate(inB):
    if s == '1':
        c.x(i+usedBits) 
c.barrier()
c.append(compare,all[:-1])
c.cx(outs[0],outs[-1]+1)
c.append(compare.inverse(),all[:-1])
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