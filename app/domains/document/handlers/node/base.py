from abc import ABC, abstractmethod


class BaseNode(ABC):
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def execute(self, state):
        pass

    def __call__(self, state):
        return self.execute(state)
