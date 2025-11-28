import deepagents_cli
import pkgutil
import inspect

print("DeepAgents CLI package path:", deepagents_cli.__path__)

def list_submodules(package):
    if hasattr(package, '__path__'):
        for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            print(module_name)

list_submodules(deepagents_cli)
