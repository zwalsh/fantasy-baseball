import importlib
import sys
from functools import reduce
from operator import add


def task_class_name(file_name):
    return reduce(add, map(str.title, file_name.split("_")))

username = sys.argv[1]
task_file_name = sys.argv[2]

task_module = importlib.import_module(f"tasks.{task_file_name}")
print(task_module)
print(dir(task_module))
task_class = getattr(task_module, task_class_name(task_file_name))
print(dir(task_class))

task = task_class.create(username)
task.execute()
