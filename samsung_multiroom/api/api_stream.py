"""
Stream messages from the speaker.
"""
import logging
import socket

from .api_response import ApiResponse

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

_LOGGER = logging.getLogger(__name__)


class ApiStream:
    """
    Speaker's api stream.

    It is possible to listen to all events/responses a speaker generates. It is useful in situations where there are
    multiple clients operating the speaker. In such case you can maintain internal state without polling.

    Once opened it will listen to messages in definitely, until interrupted using close() method.

    Example:
        stream = ApiStream('129.168.1.129')

        for response in stream.open('/UIC?cmd=%3Cname%3EGetMainInfo%3C/name%3E'):
            print(response.data)
    """

    def __init__(self, ip_address, port=55001, timeout=None):
        """
        Initialise stream.

        :param ip_address: IP address of the speaker to connect to
        :param port: Port to use, defaults to 55001
        :param timeout: Timeout in seconds
        """
        self._ip_address = ip_address
        self._port = port
        self._timeout = timeout
        self._continue_stream = False

    def open(self, uri):
        """
        Generator consuming events from speaker's main info stream.

        Yields ApiResponse instance.

        :param uri: URI to open for the stream e.g. /UIC?cmd=%3Cname%3EGetMainInfo%3C/name%3E
        """
        self._continue_stream = True

        while self._continue_stream:
            _LOGGER.debug('Opening new stream')
            try:
                parser = HttpParser()
                body = []

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self._ip_address, self._port))
                sock.settimeout(self._timeout)
                sock.send('GET {0} HTTP/1.1\r\n'.format(uri).encode())
                sock.send('Host: {0}:{1}\r\n'.format(self._ip_address, self._port).encode())
                sock.send('\r\n\r\n'.encode())

                while self._continue_stream:
                    _LOGGER.debug('Receiving from stream')
                    data = sock.recv(1024)

                    while data:
                        _LOGGER.debug('Received data: %s', data.decode())
                        received_length = len(data)
                        parsed_length = parser.execute(data, received_length)

                        if parser.is_partial_body():
                            body.append(parser.recv_body().decode())

                        if parser.is_message_complete():
                            full_body = ''.join(body)
                            parser = HttpParser()
                            body = []

                            _LOGGER.debug('Stream response: %s', full_body)

                            yield ApiResponse(full_body)

                        data = data[parsed_length:]
            except socket.error:
                _LOGGER.error('Socket exception', exc_info=1)
            finally:
                _LOGGER.debug('Closing the stream')
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

    def close(self):
        """
        Attempt to interrupt currently open stream.
        """
        _LOGGER.debug('Requested to close the stream')
        self._continue_stream = False
