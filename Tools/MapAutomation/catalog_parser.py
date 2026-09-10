"""Non-executing lexer and strict parsers for Eden configs and SQF data literals.

No eval, compile or SQF execution. Unknown syntax fails with a location.
"""
from __future__ import annotations
from dataclasses import dataclass
import re

WORD = re.compile(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[A-Za-z_$][\w$]*')


@dataclass(frozen=True)
class Token:
    value: str
    kind: str
    offset: int


def lex(text):
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith('//', i):
            j = text.find('\n', i); i = len(text) if j < 0 else j + 1
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2)
            if j < 0: raise ValueError(f'Unclosed comment at {i}')
            i = j + 2
        elif c in '\"\'':
            start, quote, buf = i, c, []; i += 1
            while i < len(text):
                if text[i] == quote:
                    if i + 1 < len(text) and text[i + 1] == quote:
                        buf.append(quote); i += 2; continue
                    i += 1; break
                buf.append(text[i]); i += 1
            else: raise ValueError(f'Unclosed string at {start}')
            out.append(Token(''.join(buf), 'string', start))
        else:
            m = WORD.match(text, i)
            value = m.group() if m else c
            kind = 'number' if m and (c.isdigit() or c == '.') else 'symbol'
            out.append(Token(value, kind, i)); i += len(value)
    return out


class Reader:
    def __init__(self, tokens, config_arrays=False):
        self.tokens, self.i, self.config_arrays = tokens, 0, config_arrays
    def peek(self):
        if self.i >= len(self.tokens): return None
        t=self.tokens[self.i]
        # A string containing "]" or "}" is data, never a closing delimiter.
        return ('string',t.value) if t.kind=='string' else t.value
    def pop(self, value=None):
        if self.i >= len(self.tokens): raise ValueError('Unexpected EOF')
        t = self.tokens[self.i]; self.i += 1
        if value is not None and (t.kind=='string' or t.value != value): raise ValueError(f'Expected {value}, got {t} ')
        return t
    def literal(self):
        t = self.pop()
        if t.kind == 'string': return t.value
        if t.kind == 'number': return float(t.value) if any(x in t.value.lower() for x in '.e') else int(t.value)
        if t.value in ('-', '+'):
            n = self.literal()
            if not isinstance(n, (int, float)): raise ValueError('Sign requires number')
            return -n if t.value == '-' else n
        if t.value.lower() in ('true', 'false'): return t.value.lower() == 'true'
        if t.value.lower() == 'any': return {'sqfUndefined': True}
        if t.value.lower() == 'createhashmapfromarray':
            pairs = self.literal()
            if not isinstance(pairs, list) or any(not isinstance(p, list) or len(p) != 2 for p in pairs):
                raise ValueError('Invalid hashmap')
            result = dict(pairs)
            if len(result) != len(pairs): raise ValueError('Duplicate hashmap key')
            return result
        if t.value == '[' or (t.value == '{' and self.config_arrays):
            close = ']' if t.value == '[' else '}'
            a = []
            while self.peek() != close:
                a.append(self.literal())
                if self.peek() == close: break
                if self.peek() not in (',', 'arg'): raise ValueError(f'Expected separator at {self.i}')
                self.pop()
            self.pop(close); return a
        raise ValueError(f'Unsupported literal {t}')


def literal(text):
    r = Reader(lex(text)); result = r.literal()
    if r.peek() is not None: raise ValueError(f'Trailing tokens at {r.i}')
    return result


def parse_config(text):
    r = Reader(lex(text), config_arrays=True)
    def body(end=None):
        node = {'properties': {}, 'children': {}}
        while r.peek() != end:
            key = r.pop().value
            if key == 'class':
                name = r.pop().value
                r.pop('{'); child = body('}'); r.pop('}'); r.pop(';')
                if name in node['children']: raise ValueError(f'Duplicate class {name}')
                node['children'][name] = child
            else:
                if r.peek() == '[': r.pop('['); r.pop(']')
                r.pop('='); value = r.literal()
                # Eden serializes multiline config strings as "a" \n "b".
                while r.peek() == '\\' and isinstance(value, str):
                    r.pop('\\'); r.pop('n'); part = r.pop()
                    if part.kind != 'string': raise ValueError('Expected continuation string')
                    value += '\n' + part.value
                r.pop(';')
                if key in node['properties']: raise ValueError(f'Duplicate property {key}')
                node['properties'][key] = value
        return node
    return body()


def parse_hashdata(text):
    r = Reader(lex(text))
    wrapped = r.peek() == 'call'
    if wrapped: r.pop('call'); r.pop('{')
    r.pop('{'); value = r.literal()
    if r.peek() == ';': r.pop(';')
    r.pop('}')
    if wrapped: r.pop('}')
    if r.peek() is not None or not isinstance(value, dict): raise ValueError('Invalid hashData wrapper')
    return value


def balanced(tokens, start, opening='(', closing=')'):
    depth = 0
    for i in range(start, len(tokens)):
        if tokens[i].kind == 'string': continue
        if tokens[i].value == opening: depth += 1
        elif tokens[i].value == closing:
            depth -= 1
            if depth == 0: return i
    raise ValueError(f'Unclosed {opening} at {start}')
