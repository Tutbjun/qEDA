from qiskit import *
#from qiskit.visualization import plot_histogram
import numpy as np

circuits = []

makeMeassurement = True
compBits = 6
stringy = '111010'
stringy = stringy[:compBits]
grovBits = compBits+1


groverBits = list(range(grovBits))
comparatorBits = list(range(grovBits,grovBits+compBits))
all = groverBits+comparatorBits
qnumbr = len(all)


encoder = QuantumCircuit(compBits,name='encoder')
nots = [i for i,e in enumerate(stringy) if e == '0']
if nots:
    encoder.x(nots)
circuits.append([encoder,comparatorBits])


hadamard = QuantumCircuit(grovBits-1, name="H")
hadamard.h(groverBits[:-1])
circuits.append([hadamard,groverBits[:-1]])

sim = QuantumCircuit(grovBits-1, name="sim")
circuits.append([sim,groverBits[:-1]])


yn = QuantumCircuit(qnumbr, name="Comparator")#!den her er pis, fix
yn.cx(comparatorBits,groverBits[:compBits])
for i in range(grovBits-1)[1:]:
    if i != 0:
        yn.x(i)
    yn.cx(groverBits[i],groverBits[i+1])
    
    
#yn.cx(1,2)
circuits.append([yn,all])

#oracle = QuantumCircuit(qnumbr, name="oracle")
#oracle.z(0,1)
#circuits.append([oracle,all])
lastBitFlipper = QuantumCircuit(1, name="Z")
lastBitFlipper.z(0)
circuits.append([lastBitFlipper,groverBits[-1:]])


circuits.append([yn.inverse(),all])

circuits.append([sim.inverse(),groverBits[:-1]])

reflection = QuantumCircuit(grovBits-1, name="reflector")
reflection.h(groverBits[:-1])
reflection.z(groverBits[:-1])
if grovBits > 2:
    reflection.cz(groverBits[:-2],groverBits[-2])
reflection.h(groverBits[:-1])
circuits.append([reflection,groverBits[:-1]])

c = QuantumCircuit(qnumbr,qnumbr)


for i,m in enumerate(circuits):
    m[0].to_gate()
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
result = backend.run(transpile(c, backend), shots=8192).result()
print(result.get_counts())
print(np.round(result.get_statevector(c),2))

#TODO: check lige om Bernstein–Vazirani algorithm kan isolere svaret