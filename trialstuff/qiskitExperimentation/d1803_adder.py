from qiskit import *
from qiskit.circuit.library.standard_gates import *
import numpy as np
usedBits = 3
qnumbr = 4*usedBits
all = list(range(qnumbr))
aList = all[0:usedBits]
bList = all[aList[-1]+1:aList[-1]+1+usedBits]
cList = all[bList[-1]+1:bList[-1]+1+usedBits]
outs = all[cList[-1]+1:cList[-1]+1+usedBits]
qr = QuantumRegister(qnumbr)
cr = ClassicalRegister(0)
compare = QuantumCircuit(qr,cr, name='comp')

#multiply by -1
#adition 
    #først en mente
    #så sæt a på b
    #hvis der var en mente fra sidst:

#notgating
#cccccx

"""for i in aList[:-1][::-1]:
    compare.cx(i,i+1)
compare.barrier()

compare.x(bList)
compare.barrier()"""

for i in range(len(aList)):
    if i !=0:

        #cccxReg = [qr[aList[i]],qr[bList[i]],qr[outs[1]],qr[outs[0],cr[1]]]
        #compare.append(C3XGate(cccxReg))
        compare.ccx(aList[i],bList[i],outs[i])
        compare.cx(aList[i],cList[i])
        compare.cx(bList[i],cList[i])
        
        compare.ccx(bList[i],outs[i-1],outs[i])
        compare.cx(outs[i-1],cList[i])

        
        #compare.ccx(bList[i],outs[1],outs[0])
        #compare.cx(outs[1],bList[0])
        #compare.cx(aList[i],bList[i])
        
        #compare.cx(outs[0],outs[1])
        #compare.ccx(outs[1],aList[1],bList[1])
        #compare.cx(outs[1],outs[0])
        #compare.ccx(aList[i-1],bList[i-1],outs[1])
        #compare.cx(outs[1],bList[i])
        
    else:
        compare.ccx(aList[i],bList[i],outs[i])
        compare.cx(aList[i],cList[i])
        compare.cx(bList[i],cList[i])
    compare.barrier()

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