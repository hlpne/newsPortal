from django import template
import re

register = template.Library()

BAD_WORDS = {"редиска"}

_WORD_RE = re.compile(r"\b([A-Za-zА-Яа-яЁё])([a-zа-яё]+)\b")


@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise TypeError("censor: expected a string")

    def repl(match: re.Match):
        first, rest = match.group(1), match.group(2)
        word = first + rest
        if rest == rest.lower():
            if word.lower() in BAD_WORDS:
                return first + ("*" * len(rest))
        return word

    return _WORD_RE.sub(repl, value)


