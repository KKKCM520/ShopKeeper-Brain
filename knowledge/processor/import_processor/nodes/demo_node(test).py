from knowledge.processor.import_processor.base import BaseNode, T


class DemoNode(BaseNode):
    def process(self, state: T) -> T:
        pass

if __name__ == '__main__':
    node = DemoNode()
    node()