import re


# at / 全角ａｔ + 全角字母数字、空格、 ideographic space、点 + 全角逗号 + 后半段
_LATIN = r"A-Za-z\uFF21-\uFF3A\uFF41-\uFF5A"
_MAIL_OBFUSCATE = re.compile(
    rf"(?<![{_LATIN}])"
    r"(?:at|\uff41\uff54)\s{1,30}"
    rf"([{_LATIN}0-9\uFF10-\uFF19\u3000\s点]{{1,30}}?)"
    r"，"
    rf"\s*([{_LATIN}0-9\uFF10-\uFF19\u3000\s]{{1,30}})"
    rf"(?![{_LATIN}])",
    re.IGNORECASE,
)


def _fullwidth_alnum_to_half(s: str) -> str:
    out: list[str] = []
    for ch in s:
        o = ord(ch)
        if 0xFF10 <= o <= 0xFF19:
            out.append(chr(o - 0xFF10 + ord("0")))
        elif 0xFF21 <= o <= 0xFF3A:
            out.append(chr(o - 0xFF21 + ord("A")))
        elif 0xFF41 <= o <= 0xFF5A:
            out.append(chr(o - 0xFF41 + ord("a")))
        elif ch == "\u3000":
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def _normalize_mail_chunk(chunk: str) -> str:
    t = _fullwidth_alnum_to_half(chunk)
    t = t.replace("点", "")
    return re.sub(r"\s+", "", t)


def mail_replace(text: str) -> str:
    """
    如果发现文本中有类似 “at 全角英文，全角英文”例如“at Q Q点，G O V”,
    替换成半角英文并删除“，”。
    """

    def _repl(m: re.Match[str]) -> str:
        g1, g2 = m.group(1), m.group(2)
        had_dot = "点" in g1
        p1 = _normalize_mail_chunk(g1)
        p2 = _normalize_mail_chunk(g2)
        body = f"{p1}.{p2}" if had_dot else f"{p1}{p2}"
        return f"at {body}"

    return _MAIL_OBFUSCATE.sub(_repl, text)

if __name__ == "__main__":
    text = "您好，欢迎致电合力亿捷，您在深圳市福田区人民法院的（二零二六）粤零三零七民初两千三百九十四号知识产权纠纷案件，已依法向您预留的邮箱九八二一四五九二六at Q Q点，C O M送达相关法律文书。您的身份证号后四位是幺三零幺。法院位置是朝南出发，经过银行后步行一百米。价格是一千九百八十八元。您看还有什么问题？欢迎和我沟通，我随时为您服务，再见。"
    print(mail_replace(text))