from __future__ import annotations
import datetime
from string import hexdigits

from fastapi import FastAPI, Response


app = FastAPI()


class ConditionBadgeGenerator:

    def __init__(
        self,
        name: str,
        color: str,
        max_hit_points: int,
        current_hit_points: int,
        flash: bool = False,
    ) -> None:
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
        self.name = name
        self.color = color
        self.max_hit_points = max_hit_points
        self.current_hit_points = current_hit_points
        self.flash = flash

        with open("./svgs/hp-frame.svg", "r", encoding="utf-8") as f:
            hp_frame = f.read()
        self.hp_frame = hp_frame
        self.svg_guage = self.guage_to_svg()
        self.svg_name = self.name_to_svg()
        self.svg_hit_points = self.hit_points_to_svg()
        self.svg_string = ""

    def reader(self, file_name: str) -> ConditionBadgeGenerator:
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

    def guage_to_svg(self) -> str:
        y = 23
        svg_guage = ""
        guage_rate = self.current_hit_points / self.max_hit_points
        guage_length = 200 * guage_rate

        if 110 <= guage_length <= 220:
            svg_guage += f'<rect x="11" y="23" width="{guage_length}" height="5" fill="green"/>'
            svg_guage += self.reader("guage-left").positioner(0, 0).replace("<rect", '<rect fill="green" ')

            if guage_length == 200:
                svg_guage += self.reader("guage-right").positioner(211, y).replace("<rect", '<rect fill="green" ')
        elif 21 <= guage_length <= 110:
            svg_guage += f'<rect x="11" y="23" width="{guage_length}" height="5" fill="yellow"/>'
            svg_guage += self.reader("guage-left").positioner(0, 0).replace("<rect", '<rect fill="yellow" ')
        else:
            if self.flash:
                svg_guage += f'<rect class="box" x="11" y="23" width="{guage_length}" height="5" fill="red"/>'
                svg_guage += self.reader("guage-left").positioner(0, 0).replace("<rect", '<rect class="box" fill="red" ')
                svg_guage += "<style>.box{animation:flash 1.5s linear infinite;}@keyframes flash{0%,100% {opacity:1;}50%{opacity:0;}}</style>"
            else:
                svg_guage += f'<rect x="11" y="23" width="{6}" height="5" fill="red"/>'
                svg_guage += self.reader("guage-left").positioner(0, 0).replace("<rect", '<rect fill="red" ')

        return svg_guage

    def name_to_svg(self) -> str:
        name_array = [i for i in self.name.upper()]
        name_array.insert(0, "colon")
        name_array_length = len(name_array)
        svg_name = ""
        x = abs(name_array_length * 8 - 215)
        y = 10
        for i in name_array:
            svg_name += self.reader(i).positioner(x, y)
            x += 8

        return svg_name

    def hit_points_to_svg(self) -> str:
        hit_points = str(self.current_hit_points) + str(self.max_hit_points)
        current_hit_points_length = len(str(self.current_hit_points))
        hit_points_array = [i for i in hit_points]
        hit_points_array.insert(current_hit_points_length, "slash")
        hit_points_length = len(hit_points_array)
        svg_max_hit_points = ""
        x = abs(hit_points_length * 8 - 215)
        y = 34
        for i in hit_points_array:
            svg_max_hit_points += self.reader(i).positioner(x, y)
            x += 8

        return svg_max_hit_points

    def hp(self) -> str:
        self.guage_to_svg()
        self.name_to_svg()
        self.hit_points_to_svg()

        svg_string = self.hp_frame.replace("<!-- name -->", self.svg_name)
        svg_string = svg_string.replace("<!-- guage -->", self.svg_guage)
        svg_string = svg_string.replace("<!-- hit points -->", self.svg_hit_points)
        return svg_string

    def mp(self) -> None:
        pass


@app.get("/")
async def main(
    name: str,
    color: str = "black",
    max: int = 10000,
    current: int = 10000,
    flash: bool = False,
) -> Response:
    color = f"#{color}" if all(c in hexdigits for c in color) else color
    current = current if current <= max else max
    svg = ConditionBadgeGenerator(name, color, max, current, flash)
    content = svg.hp()

    response_headers = {
        "Cache-Control": "no-cache",
        "Expires": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    }

    return Response(
        content=content,
        media_type="image/svg+xml",
        headers=response_headers,
    )
