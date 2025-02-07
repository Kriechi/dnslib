"""
digparser
---------

Encode/decode DNS packets from DiG textual representation. Parses
question (if present: +qr flag) & answer sections and returns list
of DNSRecord objects.

Unsupported RR types are skipped (this is different from the packet
parser which will store and encode the RDATA as a binary blob)

>>> dig = os.path.join(os.path.dirname(__file__), "..", "..", "test","data", "dig", "google.com-A.dig")
>>> with open(dig) as f:
...     l = DigParser(f)
...     for record in l:
...         print('---')
...         print(repr(record))
---
<DNS Header: id=0x5c9a type=QUERY opcode=QUERY flags=RD rcode='NOERROR' q=1 a=0 ns=0 ar=0>
<DNS Question: 'google.com.' qtype=A qclass=IN>
---
<DNS Header: id=0x5c9a type=RESPONSE opcode=QUERY flags=RD,RA rcode='NOERROR' q=1 a=16 ns=0 ar=0>
<DNS Question: 'google.com.' qtype=A qclass=IN>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.183'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.152'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.172'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.177'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.157'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.153'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.182'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.168'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.178'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.162'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.187'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.167'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.148'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.173'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.158'>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='62.252.169.163'>

>>> dig = os.path.join(os.path.dirname(__file__), "..", "..", "test", "data", "dig", "google.com-ANY.dig")
>>> with open(dig) as f:
...     l = DigParser(f)
...     for record in l:
...         print('---')
...         print(repr(record))
---
<DNS Header: id=0xb294 type=QUERY opcode=QUERY flags=RD rcode='NOERROR' q=1 a=0 ns=0 ar=0>
<DNS Question: 'google.com.' qtype=ANY qclass=IN>
---
<DNS Header: id=0xb294 type=RESPONSE opcode=QUERY flags=RD,RA rcode='NOERROR' q=1 a=14 ns=0 ar=0>
<DNS Question: 'google.com.' qtype=ANY qclass=IN>
<DNS RR: 'google.com.' rtype=A rclass=IN ttl=299 rdata='216.58.212.110'>
<DNS RR: 'google.com.' rtype=AAAA rclass=IN ttl=299 rdata='2a00:1450:4009:807::200e'>
<DNS RR: 'google.com.' rtype=CAA rclass=IN ttl=86399 rdata='0 issue "symantec.com"'>
<DNS RR: 'google.com.' rtype=MX rclass=IN ttl=599 rdata='40 alt3.aspmx.l.google.com.'>
<DNS RR: 'google.com.' rtype=MX rclass=IN ttl=599 rdata='10 aspmx.l.google.com.'>
<DNS RR: 'google.com.' rtype=NS rclass=IN ttl=86399 rdata='ns2.google.com.'>
<DNS RR: 'google.com.' rtype=MX rclass=IN ttl=599 rdata='20 alt1.aspmx.l.google.com.'>
<DNS RR: 'google.com.' rtype=SOA rclass=IN ttl=59 rdata='ns2.google.com. dns-admin.google.com. 144578247 900 900 1800 60'>
<DNS RR: 'google.com.' rtype=NS rclass=IN ttl=86399 rdata='ns1.google.com.'>
<DNS RR: 'google.com.' rtype=NS rclass=IN ttl=86399 rdata='ns4.google.com.'>
<DNS RR: 'google.com.' rtype=NS rclass=IN ttl=86399 rdata='ns3.google.com.'>
<DNS RR: 'google.com.' rtype=MX rclass=IN ttl=599 rdata='50 alt4.aspmx.l.google.com.'>
<DNS RR: 'google.com.' rtype=TXT rclass=IN ttl=3599 rdata='"v=spf1 include:_spf.google.com ~all"'>
<DNS RR: 'google.com.' rtype=MX rclass=IN ttl=599 rdata='30 alt2.aspmx.l.google.com.'>
"""

import argparse
import re
import string
import sys
import os


from dnslib.lex import WordLexer
from dnslib.dns import (
    DNSRecord,
    DNSHeader,
    DNSQuestion,
    DNSError,
    RR,
    RD,
    RDMAP,
    QR,
    RCODE,
    CLASS,
    QTYPE,
    EDNS0,
)


class DigParser:
    """
    Parse Dig output
    """

    def __init__(self, dig, debug=False):
        self.debug = debug
        self.l = WordLexer(dig)
        self.l.commentchars = ";"
        self.l.nltok = ("NL", None)
        self.i = iter(self.l)

    def parseHeader(self, l1, l2):
        _, _, _, opcode, _, status, _, _id = l1.split()
        _, flags, _ = l2.split(";")
        header = DNSHeader(id=int(_id), bitmap=0)
        header.opcode = getattr(QR, opcode.rstrip(","))
        header.rcode = getattr(RCODE, status.rstrip(","))
        for f in ("qr", "aa", "tc", "rd", "ra", "ad", "cd"):
            if f in flags:
                setattr(header, f, 1)
        return header

    def expect(self, expect):
        t, val = next(self.i)
        if t != expect:
            raise ValueError("Invalid Token: %s (expecting: %s)" % (t, expect))
        return val

    def parseQuestions(self, q, dns):
        for qname, qclass, qtype in q:
            dns.add_question(
                DNSQuestion(qname, getattr(QTYPE, qtype), getattr(CLASS, qclass))
            )

    def parseAnswers(self, a, auth, ar, dns):
        sect_map = {"a": "add_answer", "auth": "add_auth", "ar": "add_ar"}
        for sect in "a", "auth", "ar":
            f = getattr(dns, sect_map[sect])
            for rr in locals()[sect]:
                rname, ttl, rclass, rtype = rr[:4]
                rdata = rr[4:]
                rd = RDMAP.get(rtype, RD)
                try:
                    if rd == RD and any([x not in string.hexdigits for x in rdata[-1]]):
                        # Only support hex encoded data for fallback RD
                        pass
                    else:
                        f(
                            RR(
                                rname=rname,
                                ttl=int(ttl),
                                rtype=getattr(QTYPE, rtype),
                                rclass=getattr(CLASS, rclass),
                                rdata=rd.fromZone(rdata),
                            )
                        )
                except DNSError as e:
                    if self.debug:
                        print("DNSError:", e, rr)
                    else:
                        # Skip records we dont understand
                        pass

    def parseEDNS(self, edns, dns):
        args = {}
        m = re.search("version: (\d+),", edns)
        if m:
            args["version"] = int(m.group(1))
        m = re.search("flags:\s*(.*?);", edns)
        if m:
            args["flags"] = m.group(1)
        m = re.search("udp: (\d+)", edns)
        if m:
            args["udp_len"] = int(m.group(1))
        dns.add_ar(EDNS0(**args))

    def __iter__(self):
        return self.parse()

    def parse(self):
        dns = None
        section = None
        paren = False
        rr = []
        try:
            while True:
                tok, val = next(self.i)
                if tok == "COMMENT":
                    if val.startswith("; ->>HEADER<<-"):
                        # Start new record
                        if dns:
                            # If we have a current record complete this
                            self.parseQuestions(q, dns)
                            self.parseAnswers(a, auth, ar, dns)
                            yield (dns)
                        dns = DNSRecord()
                        q, a, auth, ar = [], [], [], []
                        self.expect("NL")
                        val2 = self.expect("COMMENT")
                        dns.header = self.parseHeader(val, val2)
                    elif val.startswith("; QUESTION"):
                        section = q
                    elif val.startswith("; ANSWER"):
                        section = a
                    elif val.startswith("; AUTHORITY"):
                        section = auth
                    elif val.startswith("; ADDITIONAL"):
                        section = ar
                    elif val.startswith("; OPT"):
                        #  Only partial support for parsing EDNS records
                        self.expect("NL")
                        val2 = self.expect("COMMENT")
                        self.parseEDNS(val2, dns)
                    elif val.startswith(";") or tok[1].startswith("<<>>"):
                        pass
                    elif dns and section == q:
                        q.append(val.split())
                elif tok == "ATOM":
                    if val == "(":
                        paren = True
                    elif val == ")":
                        paren = False
                    else:
                        rr.append(val)
                elif tok == "NL" and not paren and rr:
                    if self.debug:
                        print(">>", rr)
                    section.append(rr)
                    rr = []
        except StopIteration:
            if rr:
                self.section.append(rr)
            if dns:
                self.parseQuestions(q, dns)
                self.parseAnswers(a, auth, ar, dns)
                yield (dns)


def main():
    p = argparse.ArgumentParser(description="DigParser Test")
    p.add_argument(
        "--dig", action="store_true", default=False, help="Parse DiG output (stdin)"
    )
    p.add_argument("--debug", action="store_true", default=False, help="Debug output")

    args = p.parse_args()

    if args.dig:
        l = DigParser(sys.stdin, args.debug)
        for record in l:
            print(repr(record))
    else:
        import doctest, sys

        sys.exit(0 if doctest.testmod().failed == 0 else 1)


if __name__ == "__main__":
    main()
