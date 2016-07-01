#!/usr/bin/env python3

__version__ = "0.0.9"

if __name__ == "__main__":
	import send
	import recv
else:
	from filewire import send, recv
import sys
import argparse

def main():
	parser = argparse.ArgumentParser(description="Sends or receives file over LAN.")
	parser.add_argument("-v", "--verbose", help="prints verbose output", action="store_true")
	parser.add_argument("-V", "--version", help="displays version", action="store_true")
	subparsers = parser.add_subparsers(help="selection", dest="selection")
	parser_send = subparsers.add_parser("send", help="sends file", aliases=["s"])
	parser_send.add_argument("ip", type=str)
	parser_send.add_argument("file", type=str)
	parser_recv = subparsers.add_parser("recv", help="receives file", aliases=["r"])

	args = parser.parse_args()

	if len(sys.argv) == 1:
		parser.print_usage()
		return

	if args.version:
		print("filewire", __version__)
		return

	if args.selection in ["recv", "r"]:
		with recv.Receiver(verbose=args.verbose) as receiver:
			receiver.run()
	elif args.selection in ["send", "s"]:
		with send.Sender(args.ip, args.file, verbose=args.verbose) as sender:
			sender.run()

if __name__ == "__main__":
	main()
