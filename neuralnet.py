#!/usr/bin/python
#
# neuralnet.py
#
# 2014/01/18
# rg
#
# base neural networking classes

from math import exp
from utility import *
from texttable import *


class NeuralNet(object):
    # take in an array of observers, a dict of lists of weights (weights[input]=[0.1,0.2,...]) and an array
    # of output_keys
    def __init__(self, observers, weightset, output_keys):
        assert len(observers) > 0, 'must have at least one observer'
        assert len(weightset.weights) > 0, 'must have non-empty weights dict'
        assert len(output_keys) > 0, 'must have at least one output_key'

        self.observers = observers

        self.weightset = weightset

        self.outputs = {}
        for key in output_keys:
            self.outputs[key] = None

        self.input_layer = []
        self.hidden_layer = []
        self.output_layer = []

        self.create_input_layer()     # a list of Perceptrons
        self.create_hidden_layer()    # a list of Perceptrons
        self.create_output_layer()    # a list of {output_key:Perceptron} dicts

        self.validate_weights()

    def validate_weights(self):
        # ensure we have an input, hidden and output key
        assert 'input'  in self.weightset.weights, "no input  weights"
        assert 'hidden' in self.weightset.weights, "no hidden weights"
        assert 'output' in self.weightset.weights, "no output weights"

        # calculate how many inputs we have
        expected_input_count = 0
        for observer in self.observers:
            expected_input_count += observer.width

        # offload the work to the weightset
        return self.weightset.validate(expected_input_count, self.calculate_hidden_count(), len(self.outputs))

    def calculate_hidden_count(self):
        return int((len(self.input_layer) + len(self.outputs)) * 2/3)

    def create_input_layer(self):
        for observer in self.observers:
            for key in range(observer.width):
                # take advantage of the buffer key indexing (0, 1, ...) to match up with the appropriate weight
                weight = self.weightset.weights['input'][key]
                # create a uniqueish id
                myid = observer.__class__.__name__ + '-' + str(observer.id) + '-' + str(key)
                self.input_layer.append(InputPerceptron(observer, weight=weight, myid=myid, index=key))

    # create hidden neurons and attach them to each of our input neurons using the weights in weights['hidden']
    def create_hidden_layer(self):
        count = self.calculate_hidden_count()
        for i in range(count):
            hp = HiddenPerceptron(self.input_layer, self.weightset.weights['hidden'][i])
            self.hidden_layer.append(hp)

    # create output neurons and attach them to each of our hidden neurons using the weights in weights['hidden']
    def create_output_layer(self):
        count = len(self.outputs)
        for i in range(count):
            key = self.outputs.keys()[i]
            op = OutputPerceptron(self.hidden_layer, self.weightset.weights['output'][i], key)
            self.output_layer.append({key: op})

    # pulse the neural net and store the output for later use
    def pulse(self):
        # fire each output neuron
        for item in self.output_layer:
            output_key = item.keys()[0]
            output_neuron = item[output_key]
            self.outputs[output_key] = output_neuron.generate_output()

    # print a representation of the neural net
    def print_me(self):
        output = ""
        # Table 1: print input layer
        input_table = Texttable()
        input_table.set_deco(Texttable.HEADER | Texttable.BORDER)
        rows = []
        # header row
        rows.append(["Index", "Weight"])

        # data rows
        for i in range(len(self.input_layer)):
            rows.append(["in-" + str(i), self.input_layer[i].weight])

        input_table.add_rows(rows)
        output += "\n" + "-- INPUT LAYER --"
        output += input_table.draw()

        # other layers
        output += self.print_layer('HIDDEN')
        output += self.print_layer('OUTPUT')

        # ---------------------
        # Table 4: print current outputs
        output_table = Texttable()
        output_table.set_deco(Texttable.HEADER | Texttable.BORDER)
        rows = []
        # header row
        rows.append(["Output", "Value"])

        # data rows
        for key in self.outputs.keys():
            rows.append([key, self.outputs[key]])

        output_table.add_rows(rows)
        output += "\n" + "-- OUTPUT DATA --"
        output += output_table.draw()

        return output

    # layer is either hidden or output
    def print_layer(self, name):
        output = ""
        assert name == 'HIDDEN' or name == 'OUTPUT', "name must be HIDDEN or OUTPUT"
        if name == 'HIDDEN':
            our_inputs = self.input_layer
            our_layer  = self.hidden_layer
            our_input_prefix = "in-"
        elif name == 'OUTPUT':
            our_inputs = self.hidden_layer
            our_layer  = self.output_layer
            our_input_prefix = "hi-"

        rows = []
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER)

        # header row consists of each (relative) input neuron
        input_row = ["Index"]
        for i in range(len(our_inputs)):
            input_row.append(our_input_prefix + str(i))
        rows.append(input_row)

        # set column widths
        col_widths = [8]
        for i in range(len(input_row)-1):
            col_widths.append(5)
        table.set_cols_width(col_widths)

        # each row shows the weight between the row's hidden neuron and each input neuron
        for i in range(len(our_layer)):
            if name == 'HIDDEN':
                neuron_to_print = our_layer[i]
                row = ['hi-' + str(i)]
            elif name == 'OUTPUT':
                output_key = our_layer[i].keys()[0]
                neuron_to_print = our_layer[i][output_key]
                row = [output_key[:8]]

            for key in neuron_to_print.inputs.keys():
                weight = neuron_to_print.inputs[key]
                row.append(weight)
            rows.append(row)

        table.add_rows(rows)
        output += "\n" + "-- " + name + " LAYER --"
        output += table.draw()

        return output


class Perceptron(object):
    def __init__(self, myid=None):
        self.inputs = {}
        if None == myid:
            self.id = self.__repr__()
        else:
            self.id = myid

        # memoization caching
        self.memo = False

    # uplink to an upstream perceptron, storing the connection's weight in a dict
    def add_input(self, target, weight):
        self.inputs[target] = weight

    # aggregate input weights
    def step_function(self):
        return sum(self.inputs.values())

    @staticmethod
    def sigmoid(num):
        return 1 / (1 + exp(-num))

    # return the sigmoid of: the sum of our inputs multiplied by their respective weights
    def generate_output(self, indent_level=0, getlast=True):
        # use our cache, if available
        if getlast is True and self.memo is not False:
            return self.memo
        else:
            func_debug = 0
            weighted = 0
            sigmoided = 0

            if func_debug:
                indent_print(indent_level, "running generate_output() for: " + self.id)

            for each_input in self.inputs.keys():
                output = each_input.generate_output(indent_level=indent_level+1, getlast=getlast)
                weighted += self.inputs[each_input] * output
                sigmoided = Perceptron.sigmoid(weighted)
                # debug output
                if func_debug:
                    indent_print(indent_level+1, "looking at connection from " + each_input.id + " to " + self.id)
                    indent_print(indent_level+2, "input weight: " + str(self.inputs[each_input]))
                    indent_print(indent_level+2, "output: " + str(output))
                    indent_print(indent_level+2, "weighted: " + str(weighted))
                    indent_print(indent_level+2, "sigmoided: " + str(round(sigmoided, 4)))

            self.memo = sigmoided

            return sigmoided


class InputPerceptron(Perceptron):
    def __init__(self, observer, weight=None, myid=None, index=None):
        self.observer = observer
        if index is None:
            raise AssertionError("no index supplied")
        else:
            self.index = index

        if weight is None:
            raise AssertionError("no weight supplied")
        else:
            self.weight = weight

        Perceptron.__init__(self, myid)

    def generate_output(self, indent_level=0, getlast=False):
        func_debug = 0

        # ask the observer for its current sense of the world, weight it, and then run it through the sigmoid function
        sigmoided = Perceptron.sigmoid(self.sense() * self.weight)

        if func_debug:
            indent_print(indent_level, "running generate_output() for: " + self.id)
            indent_print(indent_level+1, "sigmoid(" + self.id + ".sense()) = " + str(round(sigmoided, 4)))

        return sigmoided

    # probe the observer
    def sense(self):
        # nuke our caching
        self.memo = False
        return self.observer.get_value_by_index(self.index)


class MultiInputPerceptron(Perceptron):
    def __init__(self, input_neurons, neuron_weights, myid=None):
        assert len(input_neurons) == len(neuron_weights), "must have equal number of neurons and weights"
        super(MultiInputPerceptron, self).__init__(myid=myid)

        # connect to each input neuron
        for i in range(len(input_neurons)):
            self.add_input(input_neurons[i], neuron_weights[i])


class HiddenPerceptron(MultiInputPerceptron):
    pass


class OutputPerceptron(MultiInputPerceptron):
    def __init__(self, input_neurons, neuron_weights, output_key, myid=None):
        super(OutputPerceptron, self).__init__(input_neurons, neuron_weights, myid=myid)
        self.output_key = output_key


# wrapper class for geneset that exposes the genes as an arrangement of weights
class WeightSet(object):
    def __init__(self, gene_set, num_inputs=None, num_hidden=None, num_outputs=None):
        # ensure correct args
        assert num_inputs is not None and num_hidden is not None and num_outputs is not None, "empty args"
        assert len(gene_set.genes) >= num_inputs + num_hidden * num_inputs + num_outputs * num_hidden, \
            "not enough genes to fill up our weights"

        # create structure
        self.weights = {'input': [], 'hidden': [], 'output': []}

        gene_index = 0

        # fill input layer with weights
        for _ in range(num_inputs):
            self.weights['input'].append(gene_set.genes[gene_index])
            gene_index += 1

        # fill hidden layer with weights connecting to input layer
        for i in range(num_hidden):
            self.weights['hidden'].append([])
            for _ in range(num_inputs):
                self.weights['hidden'][i].append(gene_set.genes[gene_index])
                gene_index += 1

        # fill output layer with weights connecting to input layer
        for i in range(num_outputs):
            self.weights['output'].append([])
            for _ in range(num_hidden):
                self.weights['output'][i].append(gene_set.genes[gene_index])
                gene_index += 1

    # cut out junk genes
    def prune(self, num_inputs, num_hidden, num_outputs):
        # input layer
        self.weights['input'] = self.weights['input'][:num_inputs]

        # hidden layer
        self.weights['hidden'] = self.weights['hidden'][:num_hidden]
        for i in range(len(self.weights['hidden'])):
            self.weights['hidden'][i] = self.weights['hidden'][i][:num_inputs]

        # output layer
        self.weights['output'] = self.weights['output'][:num_inputs]
        for i in range(len(self.weights['output'])):
            self.weights['output'][i] = self.weights['output'][i][:num_hidden]

    def validate(self, expected_input_count, expected_hidden_count, expected_output_count):
        # ensure we have an input, hidden and output key
        assert 'input'  in self.weights, "no input  weights"
        assert 'hidden' in self.weights, "no hidden weights"
        assert 'output' in self.weights, "no output weights"

        # ensure we have exactly one input weight per expected
        assert expected_input_count == len(self.weights['input']), "input weight mismatch"

        # ensure we have exactly one hidden list per expected
        assert expected_hidden_count == len(self.weights['hidden']), "hidden weight key mismatch"

        # ensure each hidden list has length equal to number of input neurons
        for i in range(expected_hidden_count):
            assert expected_input_count == len(self.weights['hidden'][i]), "hidden weight count mismatch"

        # ensure we have exactly one output list per output
        assert expected_output_count == len(self.weights['output']), "output weight key mismatch"

        # ensure each output list has length equal to number of hidden neurons
        for i in range(expected_output_count):
            assert expected_hidden_count == len(self.weights['output'][i]), "output weight count mismatch"

        # as long as we made it this far, we're good
        return True