from qiskit import *
#from qiskit.visualization import plot_histogram
import numpy as np

circuits = []

makeMeassurement = True
compBits = 2
stringy = '111010'
stringy = stringy[:compBits]
grovBits = compBits+3


groverBits = list(range(grovBits))
comparatorBits = list(range(grovBits,grovBits+compBits))
all = groverBits+comparatorBits
qnumbr = len(all)


encoder = QuantumCircuit(compBits,name='encoder')
nots = [i for i,e in enumerate(stringy) if e == '1']
if nots:
    encoder.x(nots)
circuits.append([encoder,comparatorBits])


hadamard = QuantumCircuit(grovBits-3, name="H")
hadamard.h(groverBits[:-3])
circuits.append([hadamard,groverBits[:-3]])

sim = QuantumCircuit(grovBits-3, name="sim")
circuits.append([sim,groverBits[:-3]])

def comparator(circuit,aList,bList,outs):
    usedBits = len(aList)
    if len(aList) != len(bList):
        return
    if len(outs) != 3:
        return
    def func(circuit : QuantumCircuit, i : int, j1 : int):
        circuit.cx(bList[i],outs[j1])
        circuit.cx(aList[i],outs[j1])
        circuit.x(outs[j1])
    commandList = []
    for i in range(usedBits):
        j1 = i%3
        j2 = (i-1)%3
        j3 = (i-2)%3
        commandList.append([])
        commandList[-1].append([func,[circuit,i,j1]])
        #commandList[-1][0](*commandList[-1][1])
        if i == 0:
            commandList[-1].append([circuit.cx,[outs[j1],outs[j2]]])
            #circuit.cx(outs[j1],outs[j2])
        else:
            """circuit.barrier()"""
            commandList[-1].append([circuit.ccx,[outs[j3],outs[j1],outs[j2]]])
            """for e in commandList[-2]:
                e[0](*e[1])
            circuit.barrier()"""
            commandList[-1].append([circuit.x,[outs[j3]]])
            #circuit.ccx(outs[j3],outs[j1],outs[j2])
            #circuit.x(outs[j3])
        commandList[-1].append([func,[circuit,i,j1]])
        for e in commandList[-1]:
            e[0](*e[1])
        #commandList[-1][0](*commandList[-1][1])
        circuit.barrier()
    if j2 != 2:
        circuit.cx(outs[j2],outs[-1])

yn = QuantumCircuit(qnumbr, name="Comparator")#!den her er pis, fix
comparator(yn,groverBits[:-3],comparatorBits,groverBits[-3:])
    
#yn.cx(1,2)
circuits.append([yn,all])

#oracle = QuantumCircuit(qnumbr, name="oracle")
#oracle.z(0,1)
#circuits.append([oracle,all])
lastBitFlipper = QuantumCircuit(1, name="Z")
lastBitFlipper.z(0)
circuits.append([lastBitFlipper,groverBits[-1:]])


circuits.append([yn.inverse(),all])

circuits.append([sim.inverse(),groverBits[:-2]])

reflection = QuantumCircuit(grovBits-2, name="reflector")
reflection.h(groverBits[:-2])
reflection.z(groverBits[:-2])
if grovBits > 2:
    reflection.cz(groverBits[:-3],groverBits[-3])
reflection.h(groverBits[:-2])
circuits.append([reflection,groverBits[:-2]])

c = QuantumCircuit(qnumbr,qnumbr)


for i,m in enumerate(circuits[:4]):
    #m[0].to_gate()
    m[0].draw(output='mpl', filename=f'out_{m[0].name}.png')
    c.append(m[0],m[1])
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