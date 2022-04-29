from qiskit import *
import numpy as np
qnumbr = 5
c = QuantumCircuit(qnumbr,qnumbr-1)
c.h(list(range(qnumbr-1)))
c.x(qnumbr-1)
c.h(qnumbr-1)
c.barrier()
c.cx(0,qnumbr-1)                 
c.barrier()
c.h(list(range(qnumbr-1)))
c.draw(output='mpl', filename='out.png')
backend = Aer.get_backend('unitary_simulator')
job = execute(c, backend)
result = job.result()
print(np.round(result.get_unitary(c, decimals=2),2))
backend = Aer.get_backend('statevector_simulator')
result = backend.run(transpile(c, backend)).result()
print(np.round(result.get_statevector(c),2))