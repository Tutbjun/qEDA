from qiskit import *
import numpy as np
usedBits = 6
qnumbr = 2*usedBits+3
all = list(range(qnumbr))
aList = all[0:usedBits]
bList = all[aList[-1]+1:aList[-1]+1+usedBits]
outs = all[bList[-1]+1:bList[-1]+4]
compare = QuantumCircuit(qnumbr,0, name='comp')


def func(circuit : QuantumCircuit, i : int, j1 : int):
    circuit.cx(bList[i],outs[j1])
    circuit.cx(aList[i],outs[j1])
    circuit.x(outs[j1])
for i in range(usedBits):
    j1 = i%3
    j2 = (i-1)%3
    j3 = (i-2)%3
    command = [func,[compare,i,j1]]
    command[0](*command[1])
    if i == 0:
        compare.cx(outs[j1],outs[j2])
    else:
        compare.ccx(outs[j3],outs[j1],outs[j2])
        compare.x(outs[j3])
    command[0](*command[1])
    compare.barrier()
if j2 != 2:
    compare.cx(outs[j2],outs[-1])

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