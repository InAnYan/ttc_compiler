class Emitter:

    full_path: str
    header: str
    code: str

    def __init__(self, full_path: str):
        self.full_path = full_path
        self.code = ''
        self.header = ''

    def emit(self, code: str):
        self.code += code

    def emit_line(self, code: str):
        self.code += code + '\n'

    def header_line(self, code: str):
        self.header += code + '\n'

    def write_file(self):
        with open(self.full_path, 'w') as fout:
            fout.write(self.header + self.code)
