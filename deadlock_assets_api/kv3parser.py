import re
import json


class KV3ParseError(Exception):
    def __init__(self, message, index, content):
        self.message = message
        self.index = index
        self.content = content
        super().__init__(self.get_error_message())

    def get_error_message(self):
        lines = self.content[: self.index].split("\n")
        line_number = len(lines)
        column = len(lines[-1]) + 1
        context_start = max(0, self.index - 20)
        context_end = min(len(self.content), self.index + 20)
        context = self.content[context_start:context_end]
        pointer = " " * (self.index - context_start) + "^"
        return f"{self.message} at line {line_number}, column {column}:\n\n{context}\n{pointer}"


class KV3Parser:
    def __init__(self, content):
        self.content = content
        self.index = 0
        self.flags = ["resource", "resourcename", "panorama", "soundevent", "subclass"]

    def parse(self):
        try:
            self.skip_header()
            return self.parse_value()
        except KV3ParseError:
            raise
        except Exception as e:
            raise KV3ParseError(str(e), self.index, self.content) from e

    def skip_header(self):
        header_pattern = r"<!-- kv3 encoding:text:version{.*?} format:generic:version{.*?} -->"
        match = re.match(header_pattern, self.content)
        if match:
            self.index = match.end()
        self.skip_whitespace()

    def skip_whitespace(self):
        while self.index < len(self.content):
            if self.content[self.index].isspace():
                self.index += 1
            elif self.content[self.index : self.index + 2] == "//":
                self.index = self.content.find("\n", self.index) + 1
            elif self.content[self.index : self.index + 2] == "/*":
                self.index = self.content.find("*/", self.index) + 2
            else:
                break

    def parse_value(self):
        self.skip_whitespace()
        if self.index >= len(self.content):
            raise KV3ParseError("Unexpected end of input", self.index, self.content)

        if self.content[self.index : self.index + 8] == "subclass":
            return self.parse_subclass()

        char = self.content[self.index]

        if char == "{":
            return self.parse_object()
        elif char == "[":
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char.isdigit() or char == "-":
            return self.parse_number()
        else:
            return self.parse_keyword_or_resource()

    def parse_subclass(self):
        self.index += 8  # Skip 'subclass'
        self.skip_whitespace()
        if self.content[self.index] != ":":
            raise KV3ParseError("Expected ':' after 'subclass'", self.index, self.content)
        self.index += 1  # Skip ':'
        self.skip_whitespace()
        if self.content[self.index] != "{":
            raise KV3ParseError("Expected '{' after 'subclass:'", self.index, self.content)
        return {"subclass": self.parse_object()}

    def parse_object(self):
        result = {}
        self.index += 1  # Skip '{'
        while True:
            self.skip_whitespace()
            if self.index >= len(self.content):
                raise KV3ParseError(
                    "Unexpected end of input while parsing object", self.index, self.content
                )

            if self.content[self.index] == "}":
                self.index += 1
                return result

            key, flag = self.parse_key()
            self.skip_whitespace()
            if self.content[self.index] == "=":
                self.index += 1
                value = self.parse_value()
            elif self.content[self.index] == "{":
                value = self.parse_object()
            else:
                value = self.parse_string()

            result[key] = {"value": value, "flag": flag} if flag else value

            self.skip_whitespace()
            if self.index >= len(self.content):
                raise KV3ParseError(
                    "Unexpected end of input while parsing object", self.index, self.content
                )

            if self.content[self.index] == ",":
                self.index += 1
            elif self.content[self.index] != "}":
                # Allow omitting commas between key-value pairs
                continue

    def parse_array(self):
        result = []
        self.index += 1  # Skip '['
        while True:
            self.skip_whitespace()
            if self.index >= len(self.content):
                raise KV3ParseError(
                    "Unexpected end of input while parsing array", self.index, self.content
                )

            if self.content[self.index] == "]":
                self.index += 1
                return result

            value = self.parse_value()
            result.append(value)

            self.skip_whitespace()
            if self.index >= len(self.content):
                raise KV3ParseError(
                    "Unexpected end of input while parsing array", self.index, self.content
                )

            if self.content[self.index] == ",":
                self.index += 1
            elif self.content[self.index] != "]":
                # Allow omitting commas in arrays
                continue

    def parse_string(self):
        if self.content[self.index : self.index + 3] == '"""':
            return self.parse_multiline_string()

        result = ""
        self.index += 1  # Skip opening quote
        while self.index < len(self.content) and self.content[self.index] != '"':
            if self.content[self.index] == "\\":
                self.index += 1
                if self.index >= len(self.content):
                    raise KV3ParseError(
                        "Unexpected end of input in string", self.index, self.content
                    )
                if self.content[self.index] == "n":
                    result += "\n"
                elif self.content[self.index] == "t":
                    result += "\t"
                else:
                    result += self.content[self.index]
            else:
                result += self.content[self.index]
            self.index += 1

        if self.index >= len(self.content):
            raise KV3ParseError("Unterminated string", self.index, self.content)

        self.index += 1  # Skip closing quote
        return result

    def parse_multiline_string(self):
        self.index += 3  # Skip opening triple quotes
        if self.content[self.index] == "\n":
            self.index += 1  # Skip newline after opening triple quotes
        start = self.index
        while (
            self.index < len(self.content) and self.content[self.index : self.index + 4] != '\n"""'
        ):
            self.index += 1

        if self.index >= len(self.content):
            raise KV3ParseError("Unterminated multi-line string", self.index, self.content)

        result = self.content[start : self.index]
        self.index += 4  # Skip closing newline and triple quotes
        return result

    def parse_number(self):
        start = self.index
        while self.index < len(self.content) and (
            self.content[self.index].isdigit() or self.content[self.index] in ".-+e"
        ):
            self.index += 1
        number_str = self.content[start : self.index]
        try:
            return int(number_str)
        except ValueError:
            try:
                return float(number_str)
            except ValueError:
                raise KV3ParseError(f"Invalid number: {number_str}", start, self.content)

    def parse_keyword_or_resource(self):
        start = self.index
        while self.index < len(self.content):
            if self.content[self.index].isspace():
                break
            if self.content[self.index] in "{}[]":
                if self.content[start : self.index].count('"') % 2 == 0:
                    break
            self.index += 1
        keyword = self.content[start : self.index].strip()

        if keyword == "true":
            return True
        elif keyword == "false":
            return False
        elif keyword == "null":
            return None
        else:
            return keyword

    def parse_key(self):
        self.skip_whitespace()
        if self.index >= len(self.content):
            raise KV3ParseError(
                "Unexpected end of input while parsing key", self.index, self.content
            )

        if self.content[self.index] == '"':
            key = self.parse_string()
        else:
            start = self.index
            while self.index < len(self.content) and (
                self.content[self.index].isalnum() or self.content[self.index] in "_"
            ):
                self.index += 1
            if start == self.index:
                raise KV3ParseError("Invalid key", start, self.content)
            key = self.content[start : self.index]

        self.skip_whitespace()
        flag = None
        if self.index < len(self.content) and self.content[self.index] == ":":
            self.index += 1
            flag_start = self.index
            while self.index < len(self.content) and self.content[self.index].isalpha():
                self.index += 1
            flag = self.content[flag_start : self.index]
            if flag not in self.flags:
                raise KV3ParseError(f"Invalid flag: {flag}", flag_start, self.content)

        return key, flag


def kv3_to_json(kv3_content):
    parser = KV3Parser(kv3_content)
    try:
        parsed_data = parser.parse()
        return json.dumps(parsed_data, indent=2)
    except KV3ParseError as e:
        print(f"Error parsing KV3: {e}")
        return None
