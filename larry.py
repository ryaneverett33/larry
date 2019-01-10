from UI import UI


class larry:
    ui = None

    def __init__(self):
        self.ui = UI(self)

    def run(self):
        self.ui.main()


if __name__ == "__main__":
    app = larry()
    app.run()
