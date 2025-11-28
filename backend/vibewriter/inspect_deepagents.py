import deepagents
import pkgutil
import inspect

print("DeepAgents package path:", deepagents.__path__)

def list_submodules(package):
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        print(module_name)

list_submodules(deepagents)
