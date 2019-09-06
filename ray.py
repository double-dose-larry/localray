# raysay is a cowsay clone, except we get a cute ray(fish) that knows some flappy quips
import sys
import textwrap
import random
from flappy_quotes import quotes

class Ray():

    def build_ray(self):
        return r"""
      ~~~ _____ ~~~ 
  \  /  ∩        ∩  \  
   \/                \ 
   /     )______(     \
  /                    \
 /       ≡      ≡       \
/        ≡      ≡        \
\                        /
 \                      /
  \ ______\    /______ /
           \  /
            \/
             ‖
             ‖
             ‖
        """
    
    def build_bubble(self, string, length=40):
        bubble = []
        lines = self._normalize_text(string, length)
        bordersize = len(lines[0])
        top_bottom_border = " " + "_" * bordersize
        bubble.append(top_bottom_border)

        for index,line in enumerate(lines):
            borders = self._get_border(lines,index)
            bubble.append(f"{borders[0]} {line} {borders[1]}")

        bubble.append(top_bottom_border)

        return "\n".join(bubble)

    def _normalize_text(self, string, length):
        lines = textwrap.wrap(string, length)
        maxlen = len(max(lines, key=len))
        return [line.ljust(maxlen) for line in lines ]

    def _get_border(self,lines,index):
        if len(lines) < 2:
            return "<",">"
        elif index == 0:
            return r"/",r"\\"
        elif index == len(lines) - 1:
            return r"\\",r"/"
        else:
            return "|", "|"

    def pull_quote(self):
        return random.choice(quotes)

    def raysay(self, string, length=40, quote=False):
        if quote:
            string += f"\n{'-'*(length - 2)}\n{self.pull_quote()}"
        return "```\n" + self.build_bubble(string, length) + self.build_ray() + "\n```"


ray = Ray()

print(ray.raysay("hello world!\n i have a lot to say the rays are going to win to day no doubt", quote=False))