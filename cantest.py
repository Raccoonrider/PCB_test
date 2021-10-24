import can

bus = can.interface.Bus(bustype = 'slcan', channel = 'COM11', bitrate = 500000)

###Запрос
##message_request_BCPU = can.Message(arbitration_id = 1, data = b"\xFF\x00\x00\x00\xFF\x80\x00\x00")
##message_request_BPLS = can.Message(arbitration_id = 9, data = b"\xFF\x00\x00\x00\x00\x0D\x0E\x00")
##
##print("Tx", bus.send(message_request_BCPU))
##input_ = bus.recv(timeout = 1)
##print("Rx", input_)
##
##print("Tx", bus.send(message_request_BPLS))
##input_ = bus.recv(timeout = 1)
##print("Rx", input_)


#Запрос
##message = can.Message(arbitration_id = 3, data = b"\xC1\x00\x00\x00\x00\x00\x00\x00")
##
##print("Tx", bus.send(message))
##input_ = bus.recv(timeout = 1)
##print("Rx", input_)

message = []
message.append (can.Message(arbitration_id = 1, data = b"\xB1\x00\x00\x00\x19\x00\x00\x00"))
message.append (can.Message(arbitration_id = 7, data = b"\xB1\x00\x00\x00\x00\x69\xab\xce"))

while True:
    bus.send(message[0])
    bus.recv(timeout = 1)
    bus.send(message[1])
    input_ = bus.recv(timeout = 1)
    print(input_.data.hex())
