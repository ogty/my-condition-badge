from __future__ import annotations


class ScalableVectorGraphics:

    def __init__(self, color: str = None) -> None:
        self.number_correspondence_table = {
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }
        self.color = color if color else "black"
        self.svg_string = ""

    def reader(self, file_name: str) -> ScalableVectorGraphics:
        if file_name.isdecimal():
            file_name = self.number_correspondence_table[file_name]

        with open(f"./svgs/{file_name}.svg", "r", encoding="utf-8") as svg_file:
            svg = svg_file.readlines()

        svg_string = "".join(svg[1:-1])
        self.svg_string = svg_string
        return self

    def positioner(self, x: int, y: int) -> str:
        svg_string = f"<g transform='translate({x},{y})'>{self.svg_string}</g>"
        return svg_string

    def wrapper(self, svg_string: str) -> str:
        start = f'<svg fill="{self.color}" xmlns="http://www.w3.org/2000/svg">'
        end = "</svg>"
        svg_string = start + svg_string + end
        return svg_string


svg = ScalableVectorGraphics("black")

max_hit_points = "OGTY" # test
max_hit_points_array = [i for i in max_hit_points]
svg_max_hit_points = ""

x = 0
y = 0
for i in max_hit_points_array:
    svg_max_hit_points += svg.reader(i).positioner(x, y)
    x += 8

print(svg.wrapper(svg_max_hit_points))
