from agent_mbpp.cli import Cli


def main() -> None:
    try:
        cli = Cli()
        
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()