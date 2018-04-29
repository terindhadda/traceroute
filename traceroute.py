#!/usr/bin/python

import optparse
import socket
import sys
import time

icmp = socket.getprotobyname('icmp')
udp = socket.getprotobyname('udp')

# calculate and return average
def average(nums):
    return round(sum(nums)/len(nums), 3)

# calculate and return standard deviation
def standard_deviation(nums):
    mean = sum(nums) / len(nums)
    differences = [x - mean for x in nums]
    sq_differences = [d ** 2 for d in differences]
    return round(sum(sq_differences), 3)

# send and receive packets
def ping(dest_name, ttl, port, max_hops, timeout):
    rtts = 0
    times = []
    curr_addr = None
    curr_name = None
    while rtts < 3:

        # create and set options for sockets
        try:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            recv_socket.settimeout(timeout)

            recv_socket.bind(("", port))
            send_socket.sendto("", (dest_name, port))

            send_time = time.time()

            # find route and calculate trip time is possible
            try:
                _, curr_addr = recv_socket.recvfrom(512)
                recv_time = time.time()
                curr_addr = curr_addr[0]

                trip_time = round((recv_time - send_time)*1000, 3)
                if trip_time is not None:
                    times.append(trip_time)
                else:
                    times.append("*")
                    sys.stdout.write("* ")
                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0]
                except socket.error:
                    curr_name = curr_addr
            except socket.timeout:
                times.append("*")
                sys.stdout.write("* ")

        # this is handled later
        except socket.error:
            pass

        # close sockets and increment rtts counter
        finally:
            if 'send_socket' in locals():
                send_socket.close()
            if 'recv_socket' in locals():
                recv_socket.close()
            rtts += 1

    return times, curr_name, curr_addr

# main function will find the traceroute to dest_name, using the options
# specified in the parameters, while satisfying third requirement
def main(dest_name, port, max_hops, timeout):
    try:
        dest_addr = socket.gethostbyname(dest_name)
        print("\nTracing route to " + dest_name  + " (" + dest_addr + "), "
            + "over a maximum of " + str(max_hops) + " hops: \n")

        ttl = 1
        while True:
            sys.stdout.write(str(ttl) + " ")
            times, curr_name, curr_addr = ping(dest_addr, ttl, port, max_hops, timeout)
            nums = []
            dropped_packets = 0
            time_string = ""
            for t in times:
                if (t == "*"):
                    dropped_packets += 1
                    time_string += str(t) + " "
                else:
                    time_string += str(t) + " ms "
                    nums.append(t)

            # if 3 packets are dropped, terminate
            if (dropped_packets == 3):
                sys.stdout.write("Request timed out.\n")
            # if a socket error occured, ICMP Type 11 and Code 0, terminate
            elif (curr_name is None or curr_addr is None):
                sys.stdout.write("Socket error.\n")
                sys.stdout.write("\nTrace complete.\n")
                return 0
            # otherwise, ICMP Type 3 and Code 3, so print route and times
            else:
                if (len(nums) > 0):
                    time_string += "avg=" + str(average(nums)) + "ms "
                    time_string += "stddev=" + str(standard_deviation(nums)) + " ms"
                    print(curr_name + " (" + curr_addr + ") " + time_string)

            # this implicitly handles ICMP messages, we don't need to parse _
            ttl += 1
            if curr_addr == dest_addr or ttl > max_hops:
                break

    except socket.gaierror:
        print("That destination or service is not known.")
        return 0

    print("\nTrace complete.\n")
    return 0

if __name__ == "__main__":

    # parser for program execution commands
    parser = optparse.OptionParser(usage="%prog [options] hostname")

    # arguments to specify port number, maximum hops and timeout value
    parser.add_option("-p", "--port", dest="port",
                      help="Port to use for socket connection [default: %default]",
                      default=33434, metavar="PORT")
    parser.add_option("-m", "--max-hops", dest="max_hops",
                      help="Max hops before giving up [default: %default]",
                      default=30, metavar="MAXHOPS")
    parser.add_option("-t", "--timeout", dest="timeout",
                      help="Timed out [default: %default]",
                      default=5, metavar="TIMEOUT")

    # input validation
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("No destination host")
    else:
        dest_name = args[0]

    # include an argument to store the timeout value
    sys.exit(main(dest_name=dest_name,
                  port=int(options.port),
                  max_hops=int(options.max_hops),
                  timeout=int(options.timeout)))
