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

class DNNArch(nn.Module):
    def __init__(self,
                 input_shape, 
                 output_shape, 
                 hidden_layers_sizes=[16, 16], 
                 device='cpu', 
                 lr=1e-4):
        
        super(DNNArch, self).__init__()
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.hidden_layers_sizes = hidden_layers_sizes

        self.device = 'cpu' # default is the cpu
        if device is 'gpu':
            if torch.cuda.is_available():
                self.device = 'cuda:0'
            
        
        # implement the actual neural network
        # first layer
        self.layers = nn.ModuleList([nn.Linear(input_shape, hidden_layers_sizes[0])]) 
        # loop over the network depth
        for i in range(1, len(hidden_layers_sizes)): 
            self.layers.append(nn.Linear(hidden_layers_sizes[i-1], hidden_layers_sizes[i]))
        # last layer
        self.layers.append(nn.Linear(hidden_layers_sizes[-1], output_shape))

        # optimizer and loss
        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss_fun = nn.MSELoss(reduction='sum')

        # put the model in the self.device
        self.to(self.device)


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

class DNNDeulingArch(nn.Module):
    def __init__(self,
                 input_shape, 
                 output_shape, 
                 hidden_layers_sizes=[16, 16], 
                 device='cpu', 
                 lr=1e-4):
        
        super(DNNDeulingArch, self).__init__()
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.hidden_layers_sizes = hidden_layers_sizes

        self.device = 'cpu' # default is the cpu
        if device is 'gpu':
            if torch.cuda.is_available():
                self.device = 'cuda:0'
            
        
        # implement the actual neural network
        # first layer
        self.layers = nn.ModuleList([nn.Linear(input_shape, hidden_layers_sizes[0])]) 
        # loop over the network depth
        for i in range(1, len(hidden_layers_sizes)): 
            self.layers.append(nn.Linear(hidden_layers_sizes[i-1], hidden_layers_sizes[i]))

        # value-advantage layer
        self.A_layer = nn.Linear(hidden_layers_sizes[-1], self.output_shape)
        self.V_layer = nn.Linear(hidden_layers_sizes[-1], 1)
        
    
        # optimizer and loss
        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss_fun = nn.MSELoss(reduction='sum')

        # put the model in the self.device
        self.to(self.device)


    def forward(self, observation):
        x = torch.Tensor(observation).to(self.device)
        batch_size = x.size(0)

        # forward loop
        for i in range(len(self.layers)-1):
            x = F.relu(self.layers[i](x))

        # now let AV-layer takes care of x 
        x_A = self.A_layer(x)
        x_V = self.V_layer(x)
        # combine both A and V layers

        # subtracted mean formula
        actions = x_V + (x_A - x_A.mean())

        return actions # actions
    

    def summary(self):
        print(self)






class DNN:
    def __init__(self,
                 input_shape, 
                 output_shape, 
                 hidden_layers_sizes=[16, 16], 
                 device='cpu', 
                 lr=1e-4):
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.hidden_layers_sizes = hidden_layers_sizes
        self.device = device
        self.lr = lr

        # change only this line to include any different architecture in pytorch
        self.model = DNNDeulingArch(input_shape=self.input_shape,
                             output_shape=self.output_shape, 
                             hidden_layers_sizes=self.hidden_layers_sizes, 
                             device=self.device,
                             lr=self.lr)

    def summary(self):
        self.model.summary()

    def predict(self, source):
        return self.model(source).detach().cpu().numpy()
    

    def fit(self, source, y, epochs=1):
        y_pred = self.model(source)
        loss = self.model.loss_fun(y_pred, torch.Tensor(y).to(self.model.device))
        self.model.optimizer.zero_grad()
        loss.backward()
        self.model.optimizer.step()

    def to_model_device(self, x):
        """ place a variable into the same device as the model    

        keyword arguments:
        x -- a variable

        return:
        A platform dependant variable placed in the same device as the model
        """

        x = torch.Tensor(x)
        x.to(self.model.device)
        return x

    def update_weights(self, dnn, smoothing=False, smoothing_factor=1e-3):
        """ Copy weights from another DNN
         
        keyword arguments:
        dnn -- another DNN must use the same lib, e.g., 
        smoothing -- if true the the weights are updated with a smoothing  factor
        smoothing_factor -- used if smoothing is true
        """
        if not smoothing:
            self.model.load_state_dict(dnn.model.state_dict())
        else:
            for param1, param2 in zip(self.model.parameters(), dnn.model.parameters()):
                param1.data.copy_(smoothing_factor * param1 + (1 - smoothing_factor) * param2)
             
if __name__ == "__main__":
    # execute only if run as a script
    pass
   
    
    

        
        






