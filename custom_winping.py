import struct
import ctypes.wintypes
import ctypes
import sys
import time
import argparse
import socket
import os


class IcmpException(OSError):
    pass


class BufferTooSmall(IcmpException):
    pass


class DestinationNetUnreachable(IcmpException):
    pass


class DestinationHostUnreachable(IcmpException):
    pass


class DestinationProtocolUnreachable(IcmpException):
    pass


class DestinationPortUnreachable(IcmpException):
    pass


class NoResources(IcmpException):
    pass


class BadOption(IcmpException):
    pass


class HardwareError(IcmpException):
    pass


class PacketTooBig(IcmpException):
    pass


class RequestTimedOut(IcmpException):
    pass


class BadRequest(IcmpException):
    pass


class BadRoute(IcmpException):
    pass


class TTLExpiredInTransit(IcmpException):
    pass


class TTLExpiredOnReassembly(IcmpException):
    pass


class ParameterProblem(IcmpException):
    pass


class SourceQuench(IcmpException):
    pass


class OptionTooBig(IcmpException):
    pass


class BadDestination(IcmpException):
    pass


class GeneralFailure(IcmpException):
    pass


errno_map = {
    11001: BufferTooSmall,
    11002: DestinationNetUnreachable,
    11003: DestinationHostUnreachable,
    11004: DestinationProtocolUnreachable,
    11005: DestinationPortUnreachable,
    11006: NoResources,
    11007: BadOption,
    11008: HardwareError,
    11009: PacketTooBig,
    11010: RequestTimedOut,
    11011: BadRequest,
    11012: BadRoute,
    11013: TTLExpiredInTransit,
    11014: TTLExpiredOnReassembly,
    11015: ParameterProblem,
    11016: SourceQuench,
    11017: OptionTooBig,
    11018: BadDestination,
    11050: GeneralFailure,
}


__all__ = [
    'ping',
    'ping6',
    'IcmpHandle',
    'Icmp6Handle',
    'IpOptionInformation',
    'IcmpEchoReply',
    'Icmp6EchoReply',
]


INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
ERROR_IO_PENDING = 997


class IPAddr(ctypes.Structure):
    _fields_ = [("S_addr", ctypes.c_ulong),
                ]

    def __str__(self):
        return socket.inet_ntoa(struct.pack("L", self.S_addr))


class in6_addr(ctypes.Structure):
    _fields_ = [("Byte", ctypes.c_ubyte * 16),
                ]

    def __str__(self):
        return socket.inet_ntop(socket.AF_INET6, bytes(self.Byte))


class sockaddr_in6(ctypes.Structure):
    _fields_ = [
        ("sin6_family", ctypes.c_short),
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_ulong),
        ("sin6_addr", in6_addr),
        ("sin6_scope_id", ctypes.c_ulong)
    ]


class IPV6_ADDRESS_EX(ctypes.Structure):
    _fields_ = [
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_ulong),
        ("sin6_addr", in6_addr),
        ("sin6_scope_id", ctypes.c_ulong)
    ]
    _pack_ = 1


class ICMPV6_ECHO_REPLY(ctypes.Structure):
    _fields_ = [
        ("Address", IPV6_ADDRESS_EX),
        ("Status", ctypes.c_ulong),
        ("RoundTripTime", ctypes.c_uint)
    ]


class IP_OPTION_INFORMATION(ctypes.Structure):
    _fields_ = [("Ttl", ctypes.c_ubyte),
                ("Tos", ctypes.c_ubyte),
                ("Flags", ctypes.c_ubyte),
                ("OptionsSize", ctypes.c_ubyte),
                ("OptionsData", ctypes.c_uint32),
                ]


class ICMP_ECHO_REPLY(ctypes.Structure):
    _fields_ = [("Address", IPAddr),
                ("Status", ctypes.c_ulong),
                ("RoundTripTime", ctypes.c_ulong),
                ("DataSize", ctypes.c_ushort),
                ("Reserved", ctypes.c_ushort),
                ("Data", ctypes.c_void_p),
                ("Options", IP_OPTION_INFORMATION),
                ]


class DUMMYUNION(ctypes.Union):
    _fields_ = [
        ("Status", ctypes.c_long),
        ("Pointer", ctypes.c_void_p),
    ]


class IO_STATUS_BLOCK(ctypes.Structure):
    _fields_ = [
        ("DUMMYUNIONNAME", DUMMYUNION),
        ("Information", ctypes.POINTER(ctypes.c_ulong))
    ]


class IpOptionInformation(object):
    def __init__(s, r):
        s.Ttl = r.Ttl
        s.Tos = r.Tos
        s.Flags = r.Flags
        s.OptionsData = ctypes.string_at(r.OptionsData, r.OptionsSize)


class IcmpEchoReply(object):
    def __init__(s, r):
        s.Address = str(r.Address)
        s.Status = r.Status
        s.RoundTripTime = r.RoundTripTime
        s.Data = ctypes.string_at(r.Data, r.DataSize)
        s.Options = IpOptionInformation(r.Options)


class Icmp6EchoReply(object):
    def __init__(s, r):
        s.Address = str(r.Address.sin6_addr)
        s.Status = r.Status
        s.RoundTripTime = r.RoundTripTime


icmp = ctypes.windll.iphlpapi
kernel = ctypes.windll.kernel32


GetLastError = ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                  use_last_error=True)(("GetLastError", kernel))


def IcmpCreateFile_errcheck(res, func, args):
    if res == INVALID_HANDLE_VALUE:
        errno = GetLastError()
        raise OSError(0, "IcmpCreateFile failed", None, errno)
    return args


IcmpCreateFile = ctypes.WINFUNCTYPE(ctypes.wintypes.HANDLE,
                                    use_last_error=True)(("IcmpCreateFile", icmp))
IcmpCreateFile.errcheck = IcmpCreateFile_errcheck

Icmp6CreateFile = ctypes.WINFUNCTYPE(ctypes.wintypes.HANDLE,
                                     use_last_error=True)(("Icmp6CreateFile", icmp))
Icmp6CreateFile.errcheck = IcmpCreateFile_errcheck


def IcmpCloseHandle_errcheck(res, func, args):
    if not res:
        errno = GetLastError()
        raise OSError(0, "IcmpCloseHandle failed", None, errno)
    return args


IcmpCloseHandle = (ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                      ctypes.wintypes.HANDLE,
                                      use_last_error=True)(
                                          ("IcmpCloseHandle", icmp), (
                                              (1, "IcmpHandle"),)))
IcmpCloseHandle.errcheck = IcmpCloseHandle_errcheck


def IcmpSendEcho_errcheck(res, func, args):
    if res == 0:
        errno = GetLastError()
        if errno in errno_map:
            raise errno_map[errno](0, "IcmpSendEcho failed", None, errno)
        else:
            raise OSError(0, "IcmpSendEcho failed", None, errno)
    return args


IcmpSendEcho = (ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                   ctypes.wintypes.HANDLE,
                                   IPAddr,
                                   ctypes.wintypes.LPVOID,
                                   ctypes.wintypes.WORD,
                                   ctypes.POINTER(IP_OPTION_INFORMATION),
                                   ctypes.wintypes.LPVOID,
                                   ctypes.wintypes.DWORD,
                                   ctypes.wintypes.DWORD,
                                   use_last_error=True)(
                                       ("IcmpSendEcho", icmp), (
                                           (1, "IcmpHandle"),
                                           (1, "DestinationAddress"),
                                           (1, "RequestData"),
                                           (1, "RequestSize"),
                                           (1, "RequestOptions"),
                                           (1, "ReplyBuffer"),
                                           (1, "ReplySize"),
                                           (1, "Timeout"))))
IcmpSendEcho.errcheck = IcmpSendEcho_errcheck


def Icmp6SendEcho2_errcheck(res, func, args):
    if res == 0:
        errno = GetLastError()
        if errno == ERROR_IO_PENDING:
            pass
        elif errno in errno_map:
            raise errno_map[errno](0, "Icmp6SendEcho2 failed", None, errno)
        else:
            raise OSError(0, "Icmp6SendEcho2 failed", None, errno)
    return args


Icmp6SendEcho2 = (ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                     ctypes.wintypes.HANDLE,
                                     ctypes.wintypes.HANDLE,
                                     ctypes.wintypes.LPVOID,
                                     ctypes.wintypes.LPVOID,
                                     ctypes.POINTER(sockaddr_in6),
                                     ctypes.POINTER(sockaddr_in6),
                                     ctypes.wintypes.LPVOID,
                                     ctypes.wintypes.WORD,
                                     ctypes.POINTER(IP_OPTION_INFORMATION),
                                     ctypes.wintypes.LPVOID,
                                     ctypes.wintypes.DWORD,
                                     ctypes.wintypes.DWORD,
                                     use_last_error=True)(
                                         ("Icmp6SendEcho2", icmp), (
                                             (1, "IcmpHandle"),
                                             (1, "Event"),
                                             (1, "ApcRoutine"),
                                             (1, "ApcContext"),
                                             (1, "SourceAddress"),
                                             (1, "DestinationAddress"),
                                             (1, "RequestData"),
                                             (1, "RequestSize"),
                                             (1, "RequestOptions"),
                                             (1, "ReplyBuffer"),
                                             (1, "ReplySize"),
                                             (1, "Timeout"))))
Icmp6SendEcho2.errcheck = Icmp6SendEcho2_errcheck


def Icmp6ParseReplies_errcheck(res, func, args):
    if res != 1:
        errno = GetLastError()
        raise OSError(0, "Icmp6ParseReplies failed", None, errno)
    return args


Icmp6ParseReplies = (ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                        ctypes.wintypes.LPVOID,
                                        ctypes.wintypes.DWORD)(
                                            ("Icmp6ParseReplies", icmp), (
                                                (1, "ReplyBuffer"),
                                                (1, "ReplySize"))))
Icmp6ParseReplies.errcheck = Icmp6ParseReplies_errcheck


class IcmpHandle(object):
    def __init__(self):
        self.handle = IcmpCreateFile()

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_tb):
        IcmpCloseHandle(self.handle)


class Icmp6Handle(object):
    def __init__(self):
        self.handle = Icmp6CreateFile()

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_tb):
        IcmpCloseHandle(self.handle)


def inet_addr(ip):
    return IPAddr(struct.unpack("L", socket.inet_aton(ip))[0])


def inet6_addr(ip):
    return sockaddr_in6(socket.AF_INET6.value,
                        0,
                        0,
                        in6_addr.from_buffer_copy(
                            socket.inet_pton(socket.AF_INET6, ip)),
                        0)


def ping(handle, address, *, timeout=1000, data=None, expected_count=10):
    address = inet_addr(address)
    if data is None:
        data = os.urandom(32)
    bufsize = (ctypes.sizeof(ICMP_ECHO_REPLY) +
               len(data) + 8) * expected_count
    buf = ctypes.create_string_buffer(bufsize)

    count = IcmpSendEcho(IcmpHandle=handle,
                         DestinationAddress=address,
                         RequestData=data,
                         RequestSize=len(data),
                         RequestOptions=None,
                         ReplyBuffer=buf,
                         ReplySize=bufsize,
                         Timeout=timeout)

    replies = ctypes.cast(buf, ctypes.POINTER(
        ICMP_ECHO_REPLY * count)).contents
    replies = [IcmpEchoReply(r) for r in replies]

    return replies


def ping6(handle, address, *, timeout=1000, data=None, expected_count=10):
    address = inet6_addr(address)
    source = inet6_addr('::')
    options = IP_OPTION_INFORMATION(128, 0, 0, 0, 0)
    if data is None:
        data = os.urandom(32)
    bufsize = (ctypes.sizeof(ICMPV6_ECHO_REPLY) + len(data) + 8 +
               ctypes.sizeof(IO_STATUS_BLOCK)) * expected_count
    buf = ctypes.create_string_buffer(bufsize)

    count = Icmp6SendEcho2(IcmpHandle=handle,
                           Event=None,
                           ApcRoutine=None,
                           ApcContext=None,
                           SourceAddress=source,
                           DestinationAddress=ctypes.byref(address),
                           RequestData=data,
                           RequestSize=len(data),
                           RequestOptions=ctypes.byref(options),
                           ReplyBuffer=buf,
                           ReplySize=bufsize,
                           Timeout=timeout)
    Icmp6ParseReplies(ReplyBuffer=buf, ReplySize=bufsize)

    replies = ctypes.cast(buf, ctypes.POINTER(
        ICMPV6_ECHO_REPLY * count)).contents
    replies = [Icmp6EchoReply(r) for r in replies]

    return replies


def winping(address, count=3):
    force_ipv4 = True
    ai_list = socket.getaddrinfo(address, 0)
    if (force_ipv4):
        target_af = socket.AF_INET if force_ipv4 else socket.AF_INET6
        ai_list = [ai for ai in ai_list if ai[0] == target_af]
    if not ai_list:
        sys.exit(3)
    ip = ai_list[0][4][0]
    af = ai_list[0][0]
    ping_fun, Handle = ((ping, IcmpHandle) if af == socket.AF_INET
                        else (ping6, Icmp6Handle))

    size = 32
    data = os.urandom(size)

    requests = 0
    responses = 0
    lost = 0
    min_rtt = float("+inf")
    max_rtt = float("-inf")
    sum_rtt = 0

    try:
        with Handle() as handle:
            while True:
                count -= 1
                try:
                    res = ping_fun(handle, ip, timeout=4000, data=data)
                except RequestTimedOut:
                    requests += 1
                    lost += 1
                except OSError as e:
                    pass
                    # print("Error: ", (e,), file=sys.stderr)
                else:
                    requests += 1
                    for rep in res:
                        if rep.Status == 0:
                            rtt = rep.RoundTripTime
                            max_rtt = max(max_rtt, rtt)
                            min_rtt = min(min_rtt, rtt)
                            sum_rtt += rtt
                            responses += 1
                        else:
                            lost += 1
                finally:
                    if count <= 0:
                        break
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass

    return_data = {
        'time': None,
        'loss': None,
        'data': ''
    }

    if requests:
        return_data['data'] += ("Ping statistics for %s:\n" % (ip,))
        return_data['data'] += ("    Packets: Sent = %d, Received = %d, Lost = %d (%.2f%% loss)\n" % (
            requests,
            responses,
            lost,
            100 * lost / requests))
        return_data['loss'] = lost

    if responses:
        return_data['data'] += ("Approximate round trip times in milli-seconds:\n")
        return_data['data'] += ("    Minimum = %dms, Maximum = %dms, Average = %sms\n" %
                                (min_rtt,
                                 max_rtt,
                                 int(round(sum_rtt / responses))))
        return_data['time'] = int(round(sum_rtt / responses))
    return return_data


if __name__ == '__main__':
    cmd = 'ping -n 3 192.168.1.1'

    host = cmd.strip().split()
    address = host[3]
    count = int(host[2])
    a = None
    try:
        a = winping(address=address, count=count)
    except Exception as e:
        print(str(e))
    if a is not None:
        print(a['data'])
        print(a['time'])
        print(a['loss'])
