## Changelog:

*   0.1     2010-09-19  Initial Release
*   0.2     2010-09-22  Minor fixes
*   0.3     2010-10-02  Add DNSLabel class to support arbitrary labels (embedded '.')
*   0.4     2012-02-26  Merge with dbslib-circuits
*   0.5     2012-09-13  Add support for RFC2136 DDNS updates
                        Patch provided by Wesley Shields <wxs@FreeBSD.org> - thanks
*   0.6     2012-10-20  Basic AAAA support
*   0.7     2012-10-20  Add initial EDNS0 support (untested)
*   0.8     2012-11-04  Add support for NAPTR, Authority RR and additional RR
                        Patch provided by Stefan Andersson (https://bitbucket.org/norox) - thanks
*   0.8.1   2012-11-05  Added NAPTR test case and fixed logic error
                        Patch provided by Stefan Andersson (https://bitbucket.org/norox) - thanks
*   0.8.2   2012-11-11  Patch to fix IPv6 formatting
                        Patch provided by Torbjorn Lonnemark (https://bitbucket.org/tobbezz) - thanks
*   0.8.3   2013-04-27  Don't parse rdata if rdlength is 0
                        Patch provided by Wesley Shields <wxs@FreeBSD.org> - thanks
*   0.9.0   2014-05-05  Major update including Py3 support (see docs)
*   0.9.1   2014-05-05  Minor fixes
*   0.9.2   2014-08-26  Fix Bimap handling of unknown mappings to avoid exception in printing
                        Add typed attributes to classes
                        Misc fixes from James Mills - thanks
*   0.9.3   2014-08-26  Workaround for argparse bug which raises AssertionError if [] is
                        present in option text (really?)
*   0.9.4   2015-04-10  Fix to support multiple strings in TXT record
                        Patch provided by James Cherry (https://bitbucket.org/james_cherry) - thanks
                        NOTE: For consistency this patch changes the 'repr' output for
                            TXT records to always be quoted
*   0.9.5   2015-10-27  Add threading & timeout handling to DNSServer
*   0.9.6   2015-10-28  Replace strftime in RRSIG formatting to avoid possible locale issues
                        Identified by Bryan Everly - thanks
*   0.9.7   2017-01-15  Sort out CAA/TYPE257 DiG parsing mismatch
*   0.9.8   2019-02-25  Force DNSKEY key to be bytes object
                        Catch Bimap __wrapped__ attr (used by inspect module in 3.7)
*   0.9.9   2019-03-19  Add support for DNSSEC flag getters/setters (from <raul@dinosec.com> - thanks)
                        Added --dnssec flags to dnslib.client & dnslib.test_decode (sets EDNS0 DO flag)
                        Added EDNS0 support to dnslib.digparser
*   0.9.10  2019-03-24  Fixes to DNSSEC support
                        Add NSEC RR support
                        Add --dnssec flag to dnslib.client & dnslib.test_decode
                        Quote/unquote non-printable characters in DNS labels
                        Update test data
                        (Thanks to <raul@dinosec.com> for help)
*   0.9.11  2019-12-17  Encode NOTIFY Opcode (Issue #26)
*   0.9.12  2019-12-17  Transition master repository to Github (Bitbucket shutting down hg)
*   0.9.13  2020-06-01  Handle truncated requests in server.py (Issue #9)
                        Replace thred.isAlive with thread.is_alive (Deprecated in Py3.9)
                        Merged Pull Request #4 (Extra options for intercept.py) - thanks to @nolanl
*   0.9.14  2020-06-09  Merged Pull Request #10 (Return doctest status via exit code)
                        Thanks to @mgorny
