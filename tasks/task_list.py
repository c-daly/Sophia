#class responsible for managing the list of tasks
# that the enhanced agent is responsible for completing
class TaskList:
    #constructor
    def __init__(self, tasks=None):
        #list of tasks
        if not tasks:
            self.tasks = []
        else:
            self.tasks = tasks

    def pop_task_from_start(self):
        task = self.tasks[0]
        self.tasks = self.tasks[1:]
        return task

    def prepend_tasks(self, tasks):
        self.tasks = tasks + self.tasks[1:]
