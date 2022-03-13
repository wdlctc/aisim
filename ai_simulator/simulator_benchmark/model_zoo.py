
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import json
#from superscaler.plan_gen import TFParser, TorchParser

class ModelZoo():
    ''' Store the available models in benchmark
    '''
    # Use a dict to store valid platform_type string
    __valid_platform = ['tensorflow', 'pytorch', 'torch']


    def __init__(self, config):
        self.__init_parser(config)
        self.__init_models(config)

    def __init_parser(self, config):
        if 'platform' not in config:
            raise ValueError("platform is not provided in config")
        if config['platform'] not in self.__valid_platform:
            raise ValueError("platform is invalid")

        if config['platform'] == 'tensorflow':
            from superscaler.plan_gen import TFParser as Parser
        elif config['platform'] == 'pytorch' or config['platform'] == 'torch':
            from superscaler.plan_gen import TorchParser as Parser
        else:
            raise ValueError("platform is invalid")

        self.parser = Parser

    def __init_models(self, config):
        self.__models = []
        self.__graph_path = {}
        self.__graph_path_multi_gpu = {}
        self.__database_path = {}
        self.__nccl_dataset = {}

        if 'baseline_path' in config:
            self.__baseline = json.load((open(config['baseline_path'])))
        else:
            self.__baseline = {}

        for c, gpu in config['enviroments'].items():
            self.__nccl_dataset[gpu] = {}
            nccl_path = config['nccl_path'] + 'nccl_' + str(gpu) + '.log'
            with open(nccl_path, 'r') as f:
                for line in f:
                    if 'sum' in line:
                        data = line.split()
                        self.__nccl_dataset[gpu][int(data[1])] = float(data[-3])

        for model in config['tasks']:
            if model in self.__models:
                raise ValueError("Idential tasks \"{}\" are simulated twice".format(task))
            else:
                self.__models.append(model)
                task = config['tasks'][model]

                if 'graph_path' not in task:
                    raise ValueError("Task \"{}\" are ininlized without graph".format(task))
                else:
                    self.set_graph_path(model, task['graph_path'])

                if 'graph_path_multi_gpu' not in task:
                    raise ValueError("Task \"{}\" are ininlized without graph_path_multi_gpu".format(task))
                else:
                    self.set_graph_path_multi_gpu(model, task['graph_path_multi_gpu'])

                if 'database_path' not in task:
                    raise ValueError("Task \"{}\" are ininlized without database_path".format(task))
                else:
                    self.set_database_path(model, task['database_path'])

    def exist_model(self, model):
        if model in self.__models:
            return True
        else:
            return False

    def get_model_list(self):
        return self.__models

    def set_graph_path(self, model, graph_path):
        self.__graph_path[model] = graph_path

    def get_graph_path(self, model):
        return self.__graph_path[model]

    def set_graph_path_multi_gpu(self, model, graph_path):
        self.__graph_path_multi_gpu[model] = graph_path

    def get_graph_path_multi_gpu(self, model):
        return self.__graph_path_multi_gpu[model]

    def set_database_path(self, model, database_path):
        self.__database_path[model] = database_path

    def get_database_path(self, model):
        return self.__database_path[model]

    def get_baseline(self):
        return self.__baseline

    def set_baseline_time(self, gpu, model, baseline_time):
        if str(gpu) in self.__baseline:
            if model in self.__baseline[str(gpu)]:
                self.__baseline[str(gpu)][model] = baseline_time

    def get_baseline_time(self, gpu, model):
        baseline_time = 1.0
        if str(gpu) in self.__baseline:
            if model in self.__baseline[str(gpu)]:
                baseline_time = self.__baseline[str(gpu)][model]
        return baseline_time

    def get_nccl_dataset(self):
        return self.__nccl_dataset