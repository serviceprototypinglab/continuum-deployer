class Hello(object):

    name = ""

    def __init__(self, name=""):
        self.name = name

    def get_name(self):
        return self.name

    def say(self):
        print("Hello %s" % self.name)


def main():
    hello = Hello("World")
    hello.say()

if __name__ == "__main__":
    # execute only if run as a script
    main()
