from humanInputDatatype import humanInput
from machineInputDatatype import machineInput
from tensorDatatype import tensor
from qDataDatatype import qData

import humanoidInterpreter
import humanoidParser
import dataExtrapolator
import input2Tensor
import edaTensorFactorizer
import resultInterpreter
import resultVisualizer


def full_qEDA_loop():
    """
    This function is the main loop of the program. It is called by the main
    function.
    """
    #get data from humanoidParser ##this is merely the frontend input stage
    parserWindow = humanoidParser.humanoidParser()
    parserWindow.run()
    humanInput = parserWindow.getData()
    #perform preprocessing on the data via humanoidInterpreter ##this is thought to be an AI stage that converts text and roudamentary specifications into a mathematically defined criteria
    data = humanoidInterpreter.interpret(humanInput)
    #extrapolate on the data with dataExtrapolator ##since it would be inposible for a human to point out what the circuit should do within the full vectorspace, this is a stage that extrapolates to the full vectorspace
    #convert the data to tensors with input2Tensor ##before only circuit criteria has been defined, this is a stage that defines a tensor from the criteria
    #then find the needed components with a quantum factorization algorithm (edaTensorFactorizer) ##this is where stuff goes down
    #the results might be a bit mathematically jumbled, so it should be postproccessed with resultInterpreter to a human vectorspace
    #visualize the results with resultVisualizer for lolz
    
def main():
    full_qEDA_loop()

if __name__ == "__main__":
    main()