"""Entry point for ssh-term."""

from ssh_term.app import SSHTermApp


def main() -> None:
    app = SSHTermApp()
    app.run()


if __name__ == "__main__":
    main()
