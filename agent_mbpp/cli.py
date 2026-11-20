import argparse
from json import JSONDecodeError

from agent_mbpp.MBPPTaskInput import MBPPTaskInput


class Cli:
    def __init__(self):
        args = self.__parse_args()

        self.__task_input = self.__parse_task_input(args.task_file)
        self.__output_path = args.output
        self.__model_name = args.model_name
        self.__provider_url = args.provider_url

    @property
    def task_input(self) -> MBPPTaskInput:
        return self.__task_input

    @property
    def output_path(self) -> str:
        return self.__output_path

    @property
    def model_name(self) -> str:
        return self.__model_name

    @property
    def provider_url(self) -> str:
        return self.__provider_url

    def __parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(prog="Agent MBPP")

        parser.add_argument("--task-file", required=True,
                            help="JSON file containing the coding tasks.")
        parser.add_argument("--output", required=True,
                            help="Output file of the LLM solution.")
        parser.add_argument("--model-name", required=True,
                            help="Name of the LLM model using for the tasks.")
        parser.add_argument("--provider-url", required=True,
                            help="API URL of the LLM provider.")

        return parser.parse_args()

    def __parse_task_input(self, tasks_path: str) -> MBPPTaskInput:
        try:
            with open(tasks_path, 'r') as f:
                content = f.read()
                return MBPPTaskInput.model_validate_json(content)
        except (FileNotFoundError, PermissionError) as e:
            raise type(e)(f"{tasks_path}: {e}") from e
        except JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {tasks_path}: {e}") from e
