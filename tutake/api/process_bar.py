from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, TimeElapsedColumn, Task, SpinnerColumn, \
    MofNCompleteColumn, ProgressColumn
from rich.text import Text


class TaskCntColumn(ProgressColumn):

    def __init__(self, field_name):
        self.field_name = field_name
        super().__init__()

    def render(self, task: "Task") -> Text:
        record_cnt = task.fields.get(self.field_name)
        if record_cnt is None:
            return Text("0", style="progress.data.speed")
        return Text(f"{record_cnt}", style="progress.data.speed")


process = Progress(TextColumn("[progress.description]{task.description}"), SpinnerColumn(), BarColumn(),
                   MofNCompleteColumn(),
                   TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeRemainingColumn(),
                   TimeElapsedColumn(), TaskCntColumn('record_cnt'), TaskCntColumn('success_cnt'),
                   TaskCntColumn('skip_cnt'), TaskCntColumn('failed_cnt'))

_task_array = []
_max_task_size = 5


def finish_task(task_id):
    _task_array.append(task_id)
    if len(_task_array) > _max_task_size:
        need_remove = _task_array[0:len(_task_array) - _max_task_size]
        for t in need_remove:
            process.remove_task(t)
            _task_array.remove(t)
        process.refresh()
