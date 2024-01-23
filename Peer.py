import threading

import TCP


if __name__ == "__main__":
    joinPublic = TCP.TCP()
    joinPublic.connect(("www.shitstorm.ovh", 12345))

    local_address = joinPublic.getsockname()
    print("Local address:", local_address)

    print("Connected to server")

    myPublicHost = joinPublic.recv_str()
    myPublicPort = joinPublic.recv_int(2, False)
    myPublicEnd = (myPublicHost, myPublicPort)
    print("public host:", myPublicEnd)

    yes = joinPublic.recv_bool()
    print("other host:", yes)

    ohost = joinPublic.recv_str()
    oport = joinPublic.recv_int(2, False)
    oend = (ohost, oport)
    print("other host:", oend)

    joinPublic.close()

    def connect_and_send():
        joinDirect = TCP.TCP()
        joinDirect.bind(local_address)
        print("je me connecte à", oend)
        joinDirect.connect(oend)
        joinDirect.send_str("hello!")

    thread1 = threading.Thread(target=connect_and_send)
    thread1.start()

    def accept_incoming():
        hostDirect = TCP.TCP()
        hostDirect.bind(local_address)

        osock = hostDirect.accept()
        print("other host connected:", osock.getpeername())
        msg = TCP.recv_str(osock)
        print("other host says:", msg)

    thread2 = threading.Thread(target=accept_incoming)
    thread2.start()

    print("END")
