from qiskit import *
#from qiskit.visualization import plot_histogram
import numpy as np
import d1903_comparator

circuits = []

makeMeassurement = True
stringLen = 2
stringy = '111010'
stringy = stringy[:stringLen]
grovBits = stringLen
compBits = 4*stringLen-1


groverBits = list(range(grovBits))
comparatorBits = list(range(grovBits,grovBits+compBits))
resultBit = list(range(comparatorBits[-1]+1,comparatorBits[-1]+2))
all = groverBits+comparatorBits+resultBit
qnumbr = len(all)


encoder = QuantumCircuit(stringLen,name='encoder')
nots = [i for i,e in enumerate(stringy) if e == '1']
if nots:
    encoder.x(nots)
circuits.append([encoder,comparatorBits[-stringLen:]])


hadamard = QuantumCircuit(grovBits, name="H")
hadamard.h(groverBits)
circuits.append([hadamard,groverBits])

sim = QuantumCircuit(grovBits, name="sim")
circuits.append([sim,groverBits])

compPrep = QuantumCircuit(grovBits+compBits, name="compPrep")
for i in range(0,grovBits+compBits):
    if i != 0 and i < stringLen:
        compPrep.swap(i,i*5)
    if i%5 == 1 and i <= stringLen*5+1:
        compPrep.swap(i,comparatorBits[-stringLen:][i//5])
circuits.append([compPrep,groverBits+comparatorBits])

comp = QuantumCircuit(grovBits+compBits, name="comp")
d1903_comparator.defComp(comp,stringLen)
circuits.append([comp,groverBits+comparatorBits])

compEval = QuantumCircuit(3, name="compEval")
compEval.x([0,1])
compEval.ccx(0,1,2)
compEval.x([0,1])
circuits.append([compEval,np.asarray(groverBits+comparatorBits+resultBit)[[2,3,-1]]])

#oracle = QuantumCircuit(qnumbr, name="oracle")
#oracle.z(0,1)
#circuits.append([oracle,all])
lastBitFlipper = QuantumCircuit(1, name="Z")
lastBitFlipper.z(0)
circuits.append([lastBitFlipper,resultBit])


circuits.append([compEval.inverse(),np.asarray(groverBits+comparatorBits+resultBit)[[2,3,-1]]])

circuits.append([comp.inverse(),groverBits+comparatorBits])

circuits.append([compPrep.inverse(),groverBits+comparatorBits])

circuits.append([sim.inverse(),groverBits])

reflection = QuantumCircuit(grovBits, name="reflector")
reflection.h(list(range(grovBits)))
reflection.z(list(range(grovBits)))
if grovBits > 2:
    reflection.cz(list(range(grovBits))[:-1],list(range(grovBits))[:-1])
reflection.h(list(range(grovBits)))
circuits.append([reflection,list(range(grovBits))])

c = QuantumCircuit(qnumbr,qnumbr)


for i,m in enumerate(circuits):
    #m[0].to_gate()
    m[0].draw(output='mpl', filename=f'out_{m[0].name}.png')
    c.append(m[0],list(m[1]))
if makeMeassurement:
    c.barrier()
    #c.measure(groverBits[:-1],groverBits[:-1])
    c.measure(all,all)


c.draw(
    output='mpl', 
    filename='out.png',
    style={
        'displaycolor': {
            'H': ('#0000cc', '#ffffff'),
            'encoder': ('#800000', '#ffffff'),
            'Comparator': ('#248f24', '#ffffff'),
            'Comparator_dg': ('#248f24', '#ffffff'),#e6e600
            'reflector': ('#248f24', '#ffffff'),
            'Z': ('#0000cc', '#ffffff'),
            'sim': ('#8600b3', '#ffffff'),
            'sim_dg': ('#8600b3', '#ffffff')}})
if not makeMeassurement:
    backend = Aer.get_backend('unitary_simulator')
    job = execute(c, backend)
    result = job.result()
    print(np.round(result.get_unitary(c, decimals=2),2))
backend = Aer.get_backend('statevector_simulator')
result = backend.run(transpile(c, backend), shots=10000).result()
counts = result.get_counts()
for k in counts.keys():
    counts[k]/=10000
print(counts)
print(np.round(result.get_statevector(c),2))

#TODO: check lige om Bernstein–Vazirani algorithm kan isolere svaret