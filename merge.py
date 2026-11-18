"""India + Nepal (+ Hindi/Nepali language) channels lai euta playlist ma merge garchha.
Source: iptv-org (free, legal, publicly available streams)."""
import urllib.request

SOURCES = [
    ("🇳🇵 Nepal",  "https://iptv-org.github.io/iptv/countries/np.m3u"),
    ("🇳🇵 Nepali (other)", "https://iptv-org.github.io/iptv/languages/nep.m3u"),
    ("🇮🇳 India",  "https://iptv-org.github.io/iptv/countries/in.m3u"),
    ("🇮🇳 Hindi (other)",  "https://iptv-org.github.io/iptv/languages/hin.m3u"),
]
OUT = "india-nepal.m3u"


def set_group(extinf, group):
    if 'group-title="' in extinf:
        start = extinf.index('group-title="') + len('group-title="')
        end = extinf.index('"', start)
        return extinf[:start] + group + extinf[end:]
    head, _, name = extinf.partition(",")
    return f'{head} group-title="{group}",{name}'


def parse(text):
    """Yields (extinf, extra_option_lines, url)."""
    extinf, extras = None, []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            extinf, extras = line, []
        elif line.startswith("#"):
            if extinf:
                extras.append(line)
        elif extinf:
            yield extinf, extras, line
            extinf, extras = None, []


def main(fetch=None):
    fetch = fetch or (lambda u: urllib.request.urlopen(u, timeout=60).read().decode("utf-8", "replace"))
    seen, out, counts = set(), ["#EXTM3U"], {}
    for group, url in SOURCES:
        try:
            text = fetch(url)
        except Exception as e:  # euta source fail bhaye pani baaki chalos
            print(f"skip {url}: {e}")
            continue
        n = 0
        for extinf, extras, stream in parse(text):
            if stream in seen:
                continue
            seen.add(stream)
            out += [set_group(extinf, group), *extras, stream]
            n += 1
        counts[group] = n
    if len(seen) == 0:
        raise SystemExit("No channels fetched - purano file nai rakhne")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(counts, "total", len(seen))


if __name__ == "__main__":
    main()
