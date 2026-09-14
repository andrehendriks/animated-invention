import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    return_code: int


class CommandError(RuntimeError):
    pass


async def run_read_only_command(*command: str, timeout: int = 15) -> CommandResult:
    """Run an allowlisted read-only command without invoking a shell."""
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as error:
        raise CommandError(f"{command[0]} is not available") from error

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except TimeoutError:
        process.kill()
        await process.communicate()
        raise CommandError(f"{command[0]} command timed out")

    result = CommandResult(stdout.decode().strip(), stderr.decode().strip(), process.returncode)
    if result.return_code:
        raise CommandError(result.stderr or f"{command[0]} exited with {result.return_code}")
    return result
