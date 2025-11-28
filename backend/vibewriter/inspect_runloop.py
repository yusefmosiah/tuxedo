import runloop_api_client
import pkgutil
import inspect

print("Runloop API Client package path:", runloop_api_client.__path__)

def list_submodules(package):
    if hasattr(package, '__path__'):
        for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            print(module_name)

list_submodules(runloop_api_client)
