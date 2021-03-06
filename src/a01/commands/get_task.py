import a01.cli
import a01.models
from a01.output import TaskBriefOutput, TaskLogOutput, SequentialOutput, CommandOutput
from a01.operations import query_tasks_async, download_recording_async, get_log_content_async
from a01.transport import AsyncSession


@a01.cli.cmd('get task', desc='Retrieve tasks information.')
@a01.cli.arg('ids', help='The task id. Support multiple IDs.', positional=True)
@a01.cli.arg('log', help='Retrieve the log of the task.', option=('-l', '--log'))
@a01.cli.arg('recording', option=('-r', '--recording'),
             help='Download the recording files in recording directory at current working directory. The recordings '
                  'are flatten with the full test path as the file name if --az-mode is not specified. If --az-mode is '
                  'set, the recording files are arranged in directory structure mimic Azure CLI source code.')
@a01.cli.arg('recording_az_mode', option=['--az-mode'],
             help='When download the recording files the files are arranged in directory structure mimic Azure CLI '
                  'source code.')
async def get_task(ids: [str],
                   log: bool = False,
                   recording: bool = False,
                   recording_az_mode: bool = False) -> CommandOutput:
    tasks = await query_tasks_async(ids)
    output = SequentialOutput()

    async with AsyncSession() as session:
        for task in tasks:
            output.append(TaskBriefOutput(task))

            if log:
                output.append(TaskLogOutput(await get_log_content_async(task.log_resource_uri, session)))

            if recording:
                await download_recording_async(task.record_resource_uri,
                                               task.identifier,
                                               recording_az_mode,
                                               session)

    return output
