from abc import ABC
from dataclasses import dataclass, field
from typing import List, NamedTuple

from gevent.subprocess import PIPE, Popen

MATH_ALLOWED_NAMES = {
    k: v for k, v in __import__("math").__dict__.items() if not k.startswith("__")
}

OS_ALLOWED_COMMANDS = ("cp", "ls", "cat", "sleep")


class CommandResult(NamedTuple):
    command: str
    result: str
    success: bool = False

    def __str__(self):
        return (
            f"Command= {self.command}, "
            f"Success= {self.success}, "
            f"Result=\n{'-' * 100}\n{self.result}"
        )


@dataclass
class BaseCommand(ABC):
    """Base command"""

    command: str

    def run(self) -> CommandResult:
        """run the command"""


@dataclass
class OSCommand(BaseCommand):
    parameters: List[str] = field(default_factory=list)

    def run(self) -> CommandResult:
        if self.command not in OS_ALLOWED_COMMANDS:
            err_msg = f"The use of '{self.command}' is not allowed"
            return CommandResult(self.command, err_msg)

        cmd = f"{self.command} {' '.join(self.parameters)}"
        cmd = cmd.strip()
        sub = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)

        if (err := sub.stderr.read()) != b"":
            return CommandResult(cmd, err.decode("utf-8"))

        res = None
        if (msg := sub.stdout.read()) != b"":
            res = msg.decode("utf-8")
        return CommandResult(cmd, res, success=True)


@dataclass
class MathCommand(BaseCommand):
    def run(self) -> CommandResult:
        """Evaluate a math expression."""
        # Compile the expression
        try:
            code = compile(self.command, "<string>", "eval")
        except SyntaxError as err:
            return CommandResult(self.command, err)

        # Validate allowed names
        for name in code.co_names:
            if name not in MATH_ALLOWED_NAMES:
                err_msg = f"The use of '{name}' is not allowed"
                return CommandResult(self.command, err_msg)

        res = eval(code, {"__builtins__": {}}, MATH_ALLOWED_NAMES)  # pylint: disable=eval-used
        return CommandResult(self.command, res, success=True)
