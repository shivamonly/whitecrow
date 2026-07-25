import sys

COLOR = True

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if COLOR else text

def red(t):    return _c("91", t)
def green(t):  return _c("92", t)
def yellow(t): return _c("93", t)
def blue(t):   return _c("94", t)
def magenta(t):return _c("95", t)
def cyan(t):   return _c("96", t)
def bold(t):   return _c("1", t)
def dim(t):    return _c("2", t)

def info(tag, msg):
    print(f"  {cyan('['+tag+']')} {msg}")

def good(tag, msg):
    print(f"  {green('[+]')} {tag}: {msg}")

def warn(tag, msg):
    print(f"  {yellow('[!]')} {tag}: {msg}")

def bad(tag, msg):
    print(f"  {red('[-]')} {tag}: {msg}")

def finding(name, url, sev):
    c = {"CRITICAL": red, "HIGH": yellow, "MEDIUM": cyan, "LOW": blue, "INFO": dim}
    s = c.get(sev.upper(), dim)(sev.upper())
    print(f"  {red('[>]')} {name} [{s}] {dim(url)}")

def phase(n, name):
    print(f"\n{cyan('═══')} Phase {n}: {bold(name)} {cyan('═'*30)}")

def section(name):
    print(f"\n  {bold(name)}")

def summary(target, elapsed, subs, hosts, findings):
    print(f"\n{cyan('═'*60)}")
    print(f"  {bold('Target')}:    {target}")
    print(f"  {bold('Time')}:     {elapsed:.2f}s")
    print(f"  {bold('Subdomains')}: {subs}")
    print(f"  {bold('Hosts')}:     {hosts}")
    print(f"  {bold('Findings')}:  {findings}")
    print(f"{cyan('═'*60)}")
