# dnslib

A library to encode/decode DNS wire-format packets supporting Python 3.6 and
above.

The library provides:

* Support for encoding/decoding DNS packets between wire format,
  python objects, and Zone/DiG textual representation (dnslib.dns)

* A server framework allowing the simple creation of custom DNS
  resolvers (dnslib.server) and a number of example servers
  created using this framework

* A number of utilities for testing (dnslib.client, dnslib.proxy,
  dnslib.intercept)


## Classes

The key DNS packet handling classes are in dnslib.dns and map to the
standard DNS packet sections:

* DNSRecord - container for DNS packet. Contains:
  - DNSHeader
  - Question section containing zero or more DNSQuestion objects
  - Answer section containing zero or more RR objects
  - Authority section containing zero or more RR objects
  - Additional section containing zero or more RR objects
* DNS RRs (resource records) contain an RR header and an RD object)
* Specific RD types are implemented as subclasses of RD
* DNS labels are represented by a DNSLabel class - in most cases
  this handles conversion to/from textual representation however
  does support arbitatry labels via a tuple of bytes objects

## Usage

To decode a DNS packet:

```
>>> packet = binascii.unhexlify(b'd5ad818000010005000000000377777706676f6f676c6503636f6d0000010001c00c0005000100000005000803777777016cc010c02c0001000100000005000442f95b68c02c0001000100000005000442f95b63c02c0001000100000005000442f95b67c02c0001000100000005000442f95b93')
>>> d = DNSRecord.parse(packet)
>>> d
<DNS Header: id=0xd5ad type=RESPONSE opcode=QUERY flags=RD,RA rcode='NOERROR' q=1 a=5 ns=0 ar=0>
<DNS Question: 'www.google.com.' qtype=A qclass=IN>
<DNS RR: 'www.google.com.' rtype=CNAME rclass=IN ttl=5 rdata='www.l.google.com.'>
<DNS RR: 'www.l.google.com.' rtype=A rclass=IN ttl=5 rdata='66.249.91.104'>
<DNS RR: 'www.l.google.com.' rtype=A rclass=IN ttl=5 rdata='66.249.91.99'>
<DNS RR: 'www.l.google.com.' rtype=A rclass=IN ttl=5 rdata='66.249.91.103'>
<DNS RR: 'www.l.google.com.' rtype=A rclass=IN ttl=5 rdata='66.249.91.147'>
```

The default text representation of the DNSRecord is in zone file format:

```
>>> print(d)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 54701
;; flags: qr rd ra; QUERY: 1, ANSWER: 5, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;www.google.com.                IN      A
;; ANSWER SECTION:
www.google.com.         5       IN      CNAME   www.l.google.com.
www.l.google.com.       5       IN      A       66.249.91.104
www.l.google.com.       5       IN      A       66.249.91.99
www.l.google.com.       5       IN      A       66.249.91.103
www.l.google.com.       5       IN      A       66.249.91.147
```

To create a DNS Request Packet:

```
>>> d = DNSRecord.question("google.com")
```

(This is equivalent to: d = DNSRecord(q=DNSQuestion("google.com") )

```
>>> d
<DNS Header: id=... type=QUERY opcode=QUERY flags=RD rcode='NOERROR' q=1 a=0 ns=0 ar=0>
<DNS Question: 'google.com.' qtype=A qclass=IN>

>>> str(DNSRecord.parse(d.pack())) == str(d)
True

>>> print(d)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: rd; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;google.com.                    IN      A

>>> d = DNSRecord.question("google.com","MX")
```

(This is equivalent to: d = DNSRecord(q=DNSQuestion("google.com",QTYPE.MX) )

```
>>> str(DNSRecord.parse(d.pack())) == str(d)
True

>>> print(d)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: rd; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;google.com.                    IN      MX
```

To create a DNS Response Packet:

```
>>> d = DNSRecord(DNSHeader(qr=1,aa=1,ra=1),
...               q=DNSQuestion("abc.com"),
...               a=RR("abc.com",rdata=A("1.2.3.4")))
>>> d
<DNS Header: id=... type=RESPONSE opcode=QUERY flags=AA,RD,RA rcode='NOERROR' q=1 a=1 ns=0 ar=0>
<DNS Question: 'abc.com.' qtype=A qclass=IN>
<DNS RR: 'abc.com.' rtype=A rclass=IN ttl=0 rdata='1.2.3.4'>
>>> str(DNSRecord.parse(d.pack())) == str(d)
True

>>> print(d)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;abc.com.                       IN      A
;; ANSWER SECTION:
abc.com.                0       IN      A       1.2.3.4
```

It is also possible to create RRs from a string in zone file format

```
>>> RR.fromZone("abc.com IN A 1.2.3.4")
[<DNS RR: 'abc.com.' rtype=A rclass=IN ttl=0 rdata='1.2.3.4'>]

(Note: this produces a list of RRs which should be unpacked if being
passed to add_answer/add_auth/add_ar etc)

>>> q = DNSRecord.question("abc.com")
>>> a = q.reply()
>>> a.add_answer(*RR.fromZone("abc.com 60 A 1.2.3.4"))
>>> print(a)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;abc.com.                       IN      A
;; ANSWER SECTION:
abc.com.                60      IN      A       1.2.3.4
```

The zone file can contain multiple entries and supports most of the normal
format defined in RFC1035 (specifically not $INCLUDE)

```
>>> z = '''
...         $TTL 300
...         $ORIGIN abc.com
...
...         @       IN      MX      10  mail.abc.com.
...         www     IN      A       1.2.3.4
...                 IN      TXT     "Some Text"
...         mail    IN      CNAME   www.abc.com.
... '''
>>> for rr in RR.fromZone(textwrap.dedent(z)):
...     print(rr)
abc.com.                300     IN      MX      10 mail.abc.com.
www.abc.com.            300     IN      A       1.2.3.4
www.abc.com.            300     IN      TXT     "Some Text"
mail.abc.com.           300     IN      CNAME   www.abc.com.
```

To create a skeleton reply to a DNS query:

```
>>> q = DNSRecord(q=DNSQuestion("abc.com",QTYPE.ANY))
>>> a = q.reply()
>>> a.add_answer(RR("abc.com",QTYPE.A,rdata=A("1.2.3.4"),ttl=60))
>>> str(DNSRecord.parse(a.pack())) == str(a)
True
>>> print(a)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;abc.com.                       IN      ANY
;; ANSWER SECTION:
abc.com.                60      IN      A       1.2.3.4
```

Add additional RRs:

```
>>> a.add_answer(RR("xxx.abc.com",QTYPE.A,rdata=A("1.2.3.4")))
>>> a.add_answer(RR("xxx.abc.com",QTYPE.AAAA,rdata=AAAA("1234:5678::1")))
>>> str(DNSRecord.parse(a.pack())) == str(a)
True
>>> print(a)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;abc.com.                       IN      ANY
;; ANSWER SECTION:
abc.com.                60      IN      A       1.2.3.4
xxx.abc.com.            0       IN      A       1.2.3.4
xxx.abc.com.            0       IN      AAAA    1234:5678::1
```

It is also possible to create a reply from a string in zone file format:

```
>>> q = DNSRecord(q=DNSQuestion("abc.com",QTYPE.ANY))
>>> a = q.replyZone("abc.com 60 IN CNAME xxx.abc.com")
>>> print(a)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;abc.com.                       IN      ANY
;; ANSWER SECTION:
abc.com.                60      IN      CNAME   xxx.abc.com.

>>> str(DNSRecord.parse(a.pack())) == str(a)
True

>>> q = DNSRecord(q=DNSQuestion("abc.com",QTYPE.ANY))
>>> a = q.replyZone(textwrap.dedent(z))
>>> print(a)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 4, AUTHORITY: 0, ADDITIONAL: 0
;; QUESTION SECTION:
;abc.com.                       IN      ANY
;; ANSWER SECTION:
abc.com.                300     IN      MX      10 mail.abc.com.
www.abc.com.            300     IN      A       1.2.3.4
www.abc.com.            300     IN      TXT     "Some Text"
mail.abc.com.           300     IN      CNAME   www.abc.com.
```

To send a DNSSEC request (EDNS OPT record with DO flag & header AD flag):

```
>>> q = DNSRecord(q=DNSQuestion("abc.com",QTYPE.A))
>>> q.add_ar(EDNS0(flags="do",udp_len=4096))
>>> q.header.ad = 1
>>> print(q)
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: ...
;; flags: rd ad; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
;; QUESTION SECTION:
;abc.com.                       IN      A
;; ADDITIONAL SECTION:
;; OPT PSEUDOSECTION
; EDNS: version: 0, flags: do; udp: 4096
```

The library also includes a simple framework for generating custom DNS
resolvers in dnslib.server (see module docs). In most cases this just
requires implementing a custom 'resolve' method which receives a question
object and returns a response.

A number of sample resolvers are provided as examples (see CLI --help):

* dnslib.fixedresolver
  - Respond to all requests with fixed response
* dnslib.zoneresolver
  - Respond from Zone file
* dnslib.shellresolver
  - Call shell script to generate response

The library includes a number of client utilities:

* DiG like client library: 
   - `python -m dnslib.client --help`

* DNS Proxy Server: 
   - `python -m dnslib.proxy --help`

* Intercepting DNS Proxy Server (replace proxy responses for specified domains): 
   - `python -m dnslib.intercept --help`

## License:

BSD

## Author:

 *   PaulC

## Master Repository/Issues:

 *   https://github.com/paulc/dnslib
