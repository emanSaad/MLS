#!/usr/bin/env python
""" 
    Deep Neural Network class using torch.nn
"""
__author__ = "AL-Tam Faroq"
__copyright__ = "Copyright 2020, UALG"
__credits__ = ["Faroq AL-Tam"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Faroq AL-Tam"
__email__ = "ftam@ualg.pt"
__status__ = "Production"
   
import torch   
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


import numpy as np

class DNN(nn.Module):
    def __init__(self, input_shape, output_shape, hidden_layers_sizes=[16, 16], device='cpu', rl=1e-4):
        
        super(DNN, self).__init__()
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.hidden_layers_sizes = hidden_layers_sizes
        self.device = device
        
        # implement the actual neural network
        # first layer
        self.layers = nn.ModuleList([nn.Linear(input_shape, hidden_layers_sizes[0])]) 
        # loop over the network depth
        for i in range(1, len(hidden_layers_sizes)): 
            self.layers.append(nn.Linear(hidden_layers_sizes[i-1], hidden_layers_sizes[i]))
        # last layer
        self.layers.append(nn.Linear(hidden_layers_sizes[-1], output_shape))
        self.to(self.device)

        # optimizer and loss
        self.optimizer = optim.Adam(self.parameters(), lr=rl)
        self.loss = nn.MSELoss(reduction='sum')

    def forward(self, observation):
        x = torch.Tensor(observation).to(self.device)

        # forward loop
        for i in range(len(self.layers)-1):
            x = F.relu(self.layers[i](x))

        # output layer    
        actions = self.layers[-1](x)

        return actions # actions

    def summary(self):
        print(self)
        


def main():
     dnn = DNN(4, 4, [32, 16])
     dnn.train()
     
if __name__ == "__main__":
    # execute only if run as a script
    main()
   
    
    

        
        







