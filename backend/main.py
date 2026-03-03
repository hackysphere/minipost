import logging

# loggers can be inherited, so this can be configured in the main file
# however, other loggers must be set up after this is run (so imports must have an init function or similar)
logging.basicConfig(
    format="{asctime} | {levelname} | {message}",
    style="{",
    level=logging.DEBUG,  # TODO: use env vars to set this
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            "./app.log",  # TODO: change file name to proper name of app
            mode="a",
        ),
    ],
)


def main():
    logging.info("loaded main app")


if __name__ == "__main__":
    main()
